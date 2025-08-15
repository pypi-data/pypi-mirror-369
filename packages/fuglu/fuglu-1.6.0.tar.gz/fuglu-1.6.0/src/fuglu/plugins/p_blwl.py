# -*- coding: UTF-8 -*-
#   Copyright Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
import traceback
import typing as tp
from fuglu.shared import PrependerPlugin, AppenderPlugin, SuspectFilter, get_default_cache, Suspect, apply_template, \
    DUNNO, DEFER, string_to_actioncode, utcnow, FileList
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DBConfig, DeclarativeBase, RESTAPIError, RESTAPIConfig, sql_alchemy_version, SQL_ALCHEMY_V1
from fuglu.extensions.aioredisext import AIORedisBaseBackend, ENABLED as REDIS_AVAILABLE, ExpiringCounter
from fuglu.asyncprocpool import get_event_loop
from fuglu.stringencode import force_uString
from fuglu.mshared import BMPRCPTMixin, BMPEOHMixin, BasicMilterPlugin, convert_return2milter
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from .sa import UserPref, GLOBALSCOPE
from collections import OrderedDict
from operator import attrgetter
import logging
import fnmatch
import ipaddress
import configparser
import os
import asyncio
import json
import functools

try:
    from domainmagic.mailaddr import email_normalise_ebl, strip_batv
    from domainmagic.validators import is_email
    from domainmagic.rbl import RBLLookup
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    def is_email(value:str) -> bool:
        return value and '@' in value
    def email_normalise_ebl(value:str) -> str:
        return value.lower()
    def strip_batv(value:str) -> str:
        return value
    DOMAINMAGIC_AVAILABLE = False

class BlockWelcomeEntry(object):
    """
    Fuglu block/welcome listing basic object
    """
    TYPE_BLOCK = 'block'
    TYPE_WELCOME = 'welcome'
    SCOPE_ANY = 'any'
    SCOPE_ENV = 'env'
    SCOPE_HDR = 'hdr'
    list_id = 0
    list_type = TYPE_WELCOME
    list_scope = SCOPE_ANY
    sender_addr = None
    sender_host = None
    netmask = -1
    scope = None
    hitcount = 0
    active = True

    block_before_welcome = True

    @staticmethod
    def _is_hostname(value):
        try:
            ipaddress.ip_network(value, False)
            return True
        except ValueError:
            return False

    def _is_wildcard(self, hostname):
        return hostname and self._is_hostname(hostname) and hostname.startswith('*')

    def __init__(self, **kw):
        for key in kw:
            if hasattr(self, key):
                value = kw[key]
                if key in ['netmask', 'hitcount', 'list_id']:
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        pass  # well... best effort.
                setattr(self, key, value)

    def __str__(self):
        return f'<BlockWelcomeEntry id={self.list_id} type={self.list_type} scope={self.scope} addr={self.sender_addr} host={self.sender_host}/{self.netmask} active={self.active}>'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.scope == other.scope \
                and self.list_type == other.list_type \
                and self.list_scope == other.list_scope \
                and self.sender_addr == other.sender_addr \
                and self.sender_host == other.sender_host \
                and self.scope == other.scope:
            return True
        return False

    def __gt__(self, other):
        if self.list_scope < other.list_scope:  # 'any' < 'env' < 'hdr'
            return True
        elif self.list_scope > other.list_scope:  # 'any' > 'env' > 'hdr'
            return False
        if self.scope is not None and other.scope is not None:
            if self.scope < other.scope:  # '$GLOBAL' < '%domain' < 'user@domain'
                return True
            elif self.scope > other.scope:  # '$GLOBAL' > '%domain' > 'user@domain'
                return False
        elif self.scope is not None and other.scope is None:
            return True
        elif self.scope is None and other.scope is not None:
            return False
        if self.list_type < other.list_type:  # 'block' < 'welcome'
            return self.block_before_welcome
        elif self.list_type > other.list_type:  # 'block' > 'welcome'
            return not self.block_before_welcome
        if self.netmask > other.netmask:  # larger netmasks have precedence
            return True
        elif self.netmask < other.netmask:
            return False
        if not self._is_wildcard(self.sender_host) and self._is_wildcard(other.sender_host):
            return True
        elif self._is_wildcard(self.sender_host) and not self._is_wildcard(other.sender_host):
            return False
        if self.sender_addr is not None and other.sender_addr is not None:
            if self.sender_addr < other.sender_addr:  # '$GLOBAL' < '%domain' < '*.wildcard' < 'user@domain'
                return True
            elif self.sender_addr > other.sender_addr:  # '$GLOBAL' > '%domain' > '*.wildcard' > 'user@domain'
                return False
        elif self.sender_addr is not None and other.sender_addr is None:
            return True
        elif self.sender_addr is None and other.sender_addr is not None:
            return False

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __lt__(self, other):
        return not self.__gt__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)


"""
    match algorithm:
    by default: more precise scope wins (and individual wl overrides global bl, but this should be configurable)
    within same scope: asc sort listtype: block before welcome (should be configurable)
    within same listtype: desc sort by bitmask first: prioritise fqdn with more labels and smaller cidr ranges
    within same bitmask: desc sort host: exact match before wildcard
    wichin same fqdn: desc sort sender: exact match before wildcard before bounce before global
    match scope + sender + host
    if sender and host are set: both must hit
    """

if SQL_EXTENSION_ENABLED:
    from sqlalchemy.sql.expression import desc, asc
    from sqlalchemy import Column
    from sqlalchemy.types import Unicode, Integer, TIMESTAMP, Boolean

    class BlockWelcomeTable(DeclarativeBase, BlockWelcomeEntry):
        """
        Fuglu block/welcome listing sql backend object
        """
        __tablename__ = 'fuglu_blwl'
        list_id = Column(Integer, primary_key=True)
        list_type = Column(Unicode(30), nullable=False)
        list_scope = Column(Unicode(30), nullable=False)
        sender_addr = Column(Unicode(255), nullable=True)
        sender_host = Column(Unicode(255), nullable=True)
        netmask = Column(Integer, nullable=False)
        scope = Column(Unicode(255), nullable=False)
        lasthit = Column(TIMESTAMP, nullable=True)
        hitcount = Column(Integer, default=0, nullable=False)
        active = Column(Boolean, default=True, nullable=False)

        def __str__(self):
            return BlockWelcomeEntry.__str__(self)
else:
    class BlockWelcomeTable(BlockWelcomeEntry):
        pass


class JsonFile(FileList):
    def __init__(self, filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=False,
                 additional_filters=None, minimum_time_between_reloads=5, key_map=''):
        self.key_map = {k: v for (k, v) in [x.split(':') for x in key_map if ':' in x]}  # convert list to tuple list to dict
        super().__init__(filename, strip, skip_empty, skip_comments, lowercase, additional_filters,
                         minimum_time_between_reloads)

    def _parse_lines(self, lines):
        listings = {}
        data = '\n'.join(lines)
        lines = json.loads(data)
        
        for item in lines:
            scope = item.get('scope')
            if scope:
                item = {self.key_map.get(k, k): v for k, v in item.items()}  # convert item keys from rest to sql naming
                listing = BlockWelcomeEntry(**item)
                if not listing.active:
                    self.logger.debug(f'jsonfile {self.filename} skipping inactive listing {listing}')
                    continue
                try:
                    listings[scope].append(listing)
                except KeyError:
                    listings[scope] = [listing]
        
        for scope in listings:
            listings[scope].sort()
            listings[scope].reverse()
        return listings
    


WELCOME = 0
BLOCK = 1
STAGE_PREPENDER = 'prepender'


class AbstractBackend(object):
    requiredvars = {}

    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.engine = self.__class__.__name__
        self.logger = logging.getLogger('fuglu.plugin.blwl.backend.%s' % self.engine)

    def __str__(self):
        return self.engine

    async def evaluate(self, suspect: Suspect, stage: str):
        raise NotImplementedError()

    def lint(self):
        raise NotImplementedError()

    def _add_tag(self, suspect: Suspect, action: tp.Any) -> None:
        if action == WELCOME:
            suspect.tags['welcomelisted'][self.engine] = True
        elif action == BLOCK:
            suspect.tags['blocklisted'][self.engine] = True
        elif action is None:
            self.logger.debug(f'{suspect.id} no listing action: {action}')

    def _set_global_tag(self, suspect: Suspect) -> None:
        suspect.set_tag('welcomelisted.global', True)

    def _get_eval_order(self, suspect: Suspect, items: tp.List[str], have_global: bool = False) -> tp.List[str]:
        evalorder = []
        for item in items:
            if item == 'global' and have_global:
                evalorder.append(GLOBALSCOPE)
            elif item == 'domain' and suspect.to_domain:
                evalorder.append(f'%{suspect.to_domain.lower()}')
            elif item == 'user' and suspect.to_address:
                evalorder.append(suspect.to_address.lower())
        return evalorder
    
    
    def _get_filtersetting(self, suspect: Suspect, setting: str, fallback = None) -> bool:
        value = suspect.get_tag('miltersettings', {}).get(email_normalise_ebl(suspect.to_address), {}).get(setting, fallback)
        if value is None:
            value = suspect.get_tag('filtersettings', {}).get('setting', fallback)
        if value is None:
            config_setting = f'{self.engine.lower()}_{setting}'
            value = self.config.getboolean(self.section, config_setting, fallback=fallback)
        return value


class FugluBlockWelcome(AbstractBackend):
    """
    This backend evaluates complex block and welcome lists based on sender, sender host and recipient.


    minimal table layout:
    list_id, list_type, list_scope, sender_addr, sender_host, netmask, scope

    ```
    CREATE TABLE `fuglu_blwl` (
      `list_id` int(11) NOT NULL AUTO_INCREMENT,
      `list_type` varchar(30) NOT NULL,
      `list_scope` varchar(30) NOT NULL DEFAULT 'any',
      `sender_addr` varchar(255) DEFAULT NULL,
      `sender_host` varchar(255) DEFAULT NULL,
      `netmask` int(8) NOT NULL DEFAULT -1,
      `scope` varchar(255) NOT NULL,
      `lasthit` timestamp NULL,
      `hitcount` int(11) NOT NULL DEFAULT 0,
      'active' int(1) NOT NULL DEFAULT 1,
      PRIMARY KEY (`list_id`),
      KEY `idx_scope` (`scope`),
      KEY `idx_sort` (`list_type`, `list_scope`, `netmask`, `sender_host`, `sender_addr`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ```

    list_type is varchar and accepts:
     * block (unwanted mail)
     * welcome (wanted mail)

    list_scope is varchar and accepts:
     * any (apply listing to envelope sender and header)
     * env (apply to envelope sender only)
     * hdr (apply to headers only)

    sender_addr is varchar and accepts:
     * null: any sender
     * empty string: bounce
     * %domain: any user in domain
     * *.domain: any user in recursively matched domain
     * user@domain: full address

    sender_host is varchar and accepts
     * null: any host
     * ip address: full ip or first ip in cidr range
     * *.fqdn: recursively matching fqdn
     * fqdn: full fqdn

    netmask is int and accepts:
     * -1: if host field is empty
     * 0-32 for ipv4
     * 0-128 for ipv6
     * 1-n for fqdn (number of labels in fqdn, including * or in other words: number of dots + 1)

    scope is varchar and accepts:
     * $GLOBAL: any recipient
     * %domain: any user in domain
     * user@domain: full address

    match algorithm:
     * by default: more precise scope wins (and individual wl overrides global bl, but this should be configurable)
     * within same scope: asc sort listtype: block before welcome (should be configurable)
     * within same listtype: desc sort by bitmask first: prioritise fqdn with more labels and smaller cidr ranges
     * within same bitmask: desc sort host: exact match before wildcard
     * wichin same fqdn: desc sort sender: exact match before wildcard before bounce before global
     * match scope + sender + host
     * if sender and host are set: both must hit

    all values (except $GLOBAL) should be lowercase

    observe mariadb asc sort order: NULL, '', $, %, *, -, 1, <, a
    """
    requiredvars = {
        'fublwl_json_file': {
            'default': "",
            'description': """json file to read records. if json file is specified it'll be the read only datasource. if restapi is defined as well they will be used to update hitcount. also cache setting will have no meaning.""",
        },
        'fublwl_restapi_endpoint': {
            'default': "",
            'description': """REST API endpoint path to block/welcome list""",
        },
        'fublwl_restapi_key_map': {
            'default': "listID:list_id, listType:list_type, listScope:list_scope, senderAddress:sender_addr, senderHost:sender_host, netmask:netmask, scope:scope, hitcount:hitcount",
            'description': """map rest:sql keys""",
        },
        'fublwl_restapi_timeout': {
            'default': "10",
            'description': "restapi http timeout",
        },
        'fublwl_dbconnection': {
            'default': '',
            'description': 'sqlalchemy db connection string mysql://user:pass@host/database?charset=utf-8',
        },
        'fublwl_usecache': {
            'default': "True",
            'description': 'Use Mem Cache. This is recommended. However, if enabled it will take up to fublwl_cache_ttl seconds until listing changes are effective.',
        },
        'fublwl_cache_ttl': {
            'default': "300",
            'description': 'how long to keep listing data in memory cache',
        },
        'fublwl_update_hitcount': {
            'default': 'True',
            'description': 'update counter and lasthit timestamp on hits',
        },
        'fublwl_block_before_welcome': {
            'default': 'True',
            'description': 'evaluate blocklist before welcomelist, can be overridden individually in filter settings',
        },
        'fublwl_eval_order': {
            'default': 'user,domain,global',
            'description:': 'in which order to evaluate [global, domain, user] listings. defaults to user before domain before global',
        },
        'fublwl_header_checks': {
            'default': '',
            'description': 'Also check specified FROM-like headers (e.g. From, Sender, Resent-From, ...)'
        },
        'fublwl_header_host_only': {
            'default': 'False',
            'description': 'only check welcome listings with host specified against header (more secure)'
        },
        'fublwl_debug': {
            'default': 'False',
            'description': 'print debug output (extra verbose)',
        },
        'fublwl_debug_rcpt': {
            'default': '',
            'description': 'print debug output (extra verbose) for recipients listed (comma separated list of emails or domains)',
        },
    }

    def __init__(self, config, section):
        super().__init__(config, section)
        self.cache = get_default_cache()
        self.engine = 'FuBLWL'
        self.jsonfile = None
        
    def _init_jsonfile(self):
        if self.jsonfile is None:
            jsonpath = self.config.get(self.section, 'fublwl_json_file')
            if jsonpath:
                key_map = self.config.getlist(self.section, 'fublwl_restapi_key_map')
                self.jsonfile = JsonFile(filename=jsonpath, key_map=key_map)
            
    def _get_sql(self, suspectid) -> tp.Dict[str, tp.List[BlockWelcomeTable]]:
        listings = {}
        connectstring = self.config.get(self.section, 'fublwl_dbconnection')
        if SQL_EXTENSION_ENABLED and connectstring:
            dbsession = get_session(connectstring)
            query = dbsession.query(BlockWelcomeTable).filter(BlockWelcomeTable.active==True)
            #query = query.order_by(desc(BlockWelcomeTable.scope))
            query = query.order_by(desc(BlockWelcomeTable.sender_addr))
            query = query.order_by(desc(BlockWelcomeTable.netmask))
            query = query.order_by(asc(BlockWelcomeTable.sender_host))  # ip before hostname
            query = query.order_by(asc(BlockWelcomeTable.list_type))
            query = query.order_by(asc(BlockWelcomeTable.list_scope))
            for listing in query.all():
                try:
                    listings[listing.scope].append(listing)
                except KeyError:
                    listings[listing.scope] = [listing]
        return listings

    def _get_rest(self, suspectid: str) -> tp.Dict[str, tp.List[BlockWelcomeEntry]]:
        listings = {}

        restapi_endpoint = self.config.get(self.section, 'fublwl_restapi_endpoint')
        if restapi_endpoint:
            restapi = RESTAPIConfig(self.config, suspectid=suspectid)
            content = restapi.get(restapi_endpoint)

            restapi_key_map = self.config.getlist(self.section, 'fublwl_restapi_key_map')
            key_map = {k: v for (k, v) in [x.split(':') for x in restapi_key_map if ':' in x]}  # convert list to tuple list to dict
            for item in content:
                item = {key_map.get(k, k): v for k, v in item.items()}  # convert item keys from rest to sql naming
                listing = BlockWelcomeEntry(**item)
                if not listing.active:
                    self.logger.debug(f'{suspectid} restapi skipping inactive listing {listing}')
                    continue
                scope = item.get('scope')
                try:
                    listings[scope].append(listing)
                except KeyError:
                    listings[scope] = [listing]
        return listings

    def _get_listings(self, suspectid: str = "") -> tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]]:
        self._init_jsonfile()
        if self.jsonfile:
            listings = self.jsonfile.get_list()
            if isinstance(listings, list):
                self.logger.error(f'{suspectid} got invalid data from jsonfile reader')
        else:
            key = 'blwl-fublwl'
            usecache = self.config.getboolean(self.section, 'fublwl_usecache')
            #self.logger.debug(f"{suspectid} Get listings, usecache={usecache}")
            listings = {}
            if usecache:
                listings = self.cache.get_cache(key) or {}
                self.logger.debug(f"{suspectid} Got {len(listings)} listings from cache")
            if not listings:
                if listings is None:
                    listings = {}
                for func in [self._get_sql, self._get_rest]:
                    self.logger.debug(f"{suspectid} No cached listings, get using function {func.__name__}")
                    items = func(suspectid)
                    #self.logger.debug(f"{suspectid} Got items: {items}")
                    for scope in items:
                        try:
                            listings[scope].extend(items[scope])
                        except KeyError:
                            listings[scope] = items[scope]
                        #self.logger.debug(f"{suspectid} scope={scope} has {len(listings[scope])} elements after adding {len(items[scope])}")
                for scope in listings:
                    listings[scope] = sorted(listings[scope])
                if listings:
                    cachettl = self.config.getint(self.section, 'fublwl_cache_ttl')
                    self.cache.put_cache(key, listings, ttl=cachettl)
        return listings

    def _subnet_of(self, inner, outer) -> bool:
        try:  # python >= 3.7
            subnet_of = getattr(inner, 'subnet_of')
            return subnet_of(outer)
        except TypeError:  # check if ipv6 addr is in ipv4 net or vice versa
            return False
        except AttributeError:
            for ip in inner:
                if ip not in outer:
                    return False
        return True

    def _parse_host(self, listing: tp.Union[BlockWelcomeEntry, BlockWelcomeTable]):
        listing_net = listing_host = None
        try:
            listing_net = ipaddress.ip_network(f'{listing.sender_host}/{listing.netmask}', False)
        except ValueError:
            listing_host = listing.sender_host.lower()
        return listing_net, listing_host

    def _check_listings(self, check_listings, sender_address, sender_hostname, sender_hostip, listscope, suspectid: str = "", debug:bool=False):
        if sender_address:
            sender_address = sender_address.lower()
            sender_domain = sender_address.rsplit('@', 1)[-1]
            sender_domain_pct = f'%{sender_domain}'
            sender_domain_dot = f'.{sender_domain}'
        else:
            sender_domain_pct = None
            sender_domain_dot = None

        if sender_hostname:
            sender_hostname = sender_hostname.lower()
            sender_hostname_dot = f'.{sender_hostname}'
        else:
            sender_hostname_dot = None

        if sender_hostip:
            sender_hostip = ipaddress.ip_network(sender_hostip, False)
        self.logger.debug(f"{suspectid} sender_domain_pct={sender_domain_pct} sender_domain_dot={sender_domain_dot} sender_hostip={sender_hostip} sender_host={sender_hostname} sender_host_dot={sender_hostname_dot} listings={len(check_listings)}")

        for listing in check_listings:
            debug and self.logger.debug(f"{suspectid} checking {listing}")
            if not listing.list_scope in (BlockWelcomeEntry.SCOPE_ANY, listscope):
                debug and self.logger.debug(f"{suspectid} checking listing: {listing} "
                                            f"-> skip due to listscope {listing.list_scope} "
                                            f"not in scopes {BlockWelcomeEntry.SCOPE_ANY}, {listscope}")
                continue
            if listing.sender_addr is None and listing.sender_host is None:  # would allow any sender from any host
                debug and self.logger.debug(f"{suspectid} checking listing: {listing} "
                                  f"-> skip because listing sender address is none ({listing.sender_addr}) "
                                  f"and listing sender host is none ({listing.sender_host})")
                continue

            sender_ok = False
            host_ok = False

            if listing.sender_addr == '' and not sender_address:  # bounces
                sender_ok = True
            elif listing.sender_addr is None:  # any sender
                sender_ok = True
            elif listing.sender_addr and sender_address:
                listing_addr = listing.sender_addr.lower()
                if listing_addr == sender_address or listing_addr == sender_domain_pct:  # exact match
                    sender_ok = True
                elif sender_domain_dot and listing_addr.startswith('*.') and fnmatch.fnmatch(sender_domain_dot, listing_addr):  # wildcard match
                    sender_ok = True

            if not sender_ok:  # it'll never hit, save some cpu cycles
                debug and self.logger.debug(f"{suspectid} sender_ok={sender_ok} listing_sender_addr={listing.sender_addr} "
                                            f"sender_address={sender_address} -> continue search for listing")
                continue

            if not listing.sender_host:  # any host
                host_ok = True
            else:
                listing_net, listing_host = self._parse_host(listing)
                debug and self.logger.debug(f"{suspectid} listing_net={listing_net} listing_host={listing_host}")
                if sender_hostip and listing_net and self._subnet_of(sender_hostip, listing_net):  # ip/cidr match
                    host_ok = True
                elif not listing_net and listing_host and listing_host == sender_hostname:  # hostname exact match
                    host_ok = True
                elif not listing_net and listing_host and sender_hostname_dot \
                        and listing_host.startswith('*.') and fnmatch.fnmatch(sender_hostname_dot, listing_host):
                    host_ok = True

            if sender_ok and host_ok:
                debug and self.logger.debug(f"{suspectid} sender_ok={sender_ok} host_ok={host_ok} -> return listing: {listing}")
                return listing
            else:
                debug and self.logger.debug(f"{suspectid} sender_ok={sender_ok} host_ok={host_ok} -> continue search for listing")
        return None

    def _sort_listings(self,
                       suspect: Suspect,
                       all_listings: tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]],
                       scopes: tp.List[str]) -> tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]:
        block_before_welcome = self._get_filtersetting(suspect, 'block_before_welcome', True)
        check_listings = []
        for scope in scopes:
            scope_listings = all_listings.get(scope, [])
            if scope_listings and not block_before_welcome:
                scope_listings = sorted(scope_listings, key=attrgetter('list_type'), reverse=True)
            check_listings.extend(scope_listings)
        return check_listings
    
    def _do_debug(self, suspect):
        debug = self.config.getboolean(self.section, 'fublwl_debug')
        if not debug:
            rcpts = self.config.getlist(self.section, 'fublwl_debug_rcpt', lower=True)
            debug = suspect.to_address.lower() in rcpts or suspect.to_domain.lower() in rcpts
        return debug

    def _check_user_listings(self,
                             suspect: Suspect,
                             all_listings: tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]],
                             stage: str) -> tp.Tuple[tp.Union[BlockWelcomeEntry, BlockWelcomeTable], str]:
        eval_order = self._get_eval_order(suspect, self.config.getlist(self.section, 'fublwl_eval_order', lower=True), have_global=True)
        check_listings = self._sort_listings(suspect, all_listings, eval_order)
        debug = self._do_debug(suspect)
        if debug:
            self.logger.debug(f"{suspect.id} stage={stage} debug output enabled for {suspect.to_address}")
            self.logger.debug(f"{suspect.id} stage={stage} {check_listings}")
        
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            helo, clientip, clienthostname = clientinfo
        else:
            helo, clientip, clienthostname = None, None, None

        sender_address = suspect.from_address
        list_scope = BlockWelcomeEntry.SCOPE_ENV
        listing = None

        # check envelope sender in eoh stage only if no check was run in rcpt stage
        if stage in [asm.RCPT, STAGE_PREPENDER] or stage == asm.EOH and not asm.RCPT in suspect.get_tag('listing.stages', []):
            #self.logger.debug(f"{suspect.id} Check listings with: sender={sender_address}, clienthostname={clienthostname}, clientip={clientip}, list_scope={list_scope}, listings={check_listings}")
            listing = self._check_listings(check_listings, sender_address, clienthostname, clientip, list_scope, suspect.id, debug)
            self.logger.debug(f"{suspect.id} stage={stage} Check listings returned: {listing} for list_scope {list_scope}")
            try:
                suspect.tags['listing.stages'].append(stage)
            except KeyError:
                suspect.tags['listing.stages'] = [stage]
        if not listing and stage in [asm.EOH, STAGE_PREPENDER]:
            header = None
            list_scope = BlockWelcomeEntry.SCOPE_HDR
            headers = self.config.getlist(self.section, 'fublwl_header_checks')
            if self.config.getboolean(self.section, 'fublwl_header_host_only'):
                check_listings = [l for l in check_listings if l.sender_host or l.list_type == BlockWelcomeEntry.TYPE_BLOCK]
            for header in headers:
                hdr_addresses = [item[1] for item in suspect.parse_from_type_header(header=header, validate_mail=True)]
                self.logger.debug(f'{suspect.id} checking {len(check_listings)} listings against header {header} with addresses {",".join(hdr_addresses)}')
                for sender_address in hdr_addresses:
                    listing = self._check_listings(check_listings, sender_address, clienthostname, clientip, list_scope, suspect.id, debug)
                    if listing:
                        break
                if listing:
                    break
            self.logger.debug(f'{suspect.id} Check listings returned: {listing} for list_scope {list_scope} in header {header}')
        return listing, list_scope

    def _update_hit_count_sql(self, suspect: Suspect, listing: BlockWelcomeTable):
        list_id = listing.list_id
        try:
            connectstring = self.config.get(self.section, 'fublwl_dbconnection')
            if connectstring:
                session = get_session(connectstring)
                listing = session.query(BlockWelcomeTable).filter_by(BlockWelcomeTable.list_id == list_id).first()
                if listing is None:
                    self.logger.warning(f'{suspect.id} Cannot update listing with id {list_id} - not found')
                    return
                listing.hitcount += 1
                listing.lasthit = utcnow()  # utc timestamp wit +00:00
                session.flush()
                if sql_alchemy_version == SQL_ALCHEMY_V1:
                    session.remove()
                self.logger.debug(f'{suspect.id} updated hitcount of listing {listing.list_id} via sql')
        except Exception as e:
            self.logger.error(f'{suspect.id} Updating hitcount of listing {list_id} via sql failed: {e.__class__.__name__}: {str(e)}')

    def _update_hit_count_rest(self, suspect: Suspect, listing: BlockWelcomeEntry):
        restapi_endpoint = self.config.get(self.section, 'fublwl_restapi_endpoint')
        if restapi_endpoint:
            restapi = RESTAPIConfig(self.config, suspect.id)

            data = {
                "lasthit": utcnow().isoformat(timespec='milliseconds').rsplit('+',1)[0] + 'Z',  # utc timestamp without +00:00
                "hitcount": 1
            }
            endpoint = f'{restapi_endpoint}/{listing.list_id}'
            timeout = self.config.getfloat(self.section, 'fublwl_restapi_timeout')
            try:
                response = restapi.put(endpoint, data, timeout=timeout)
                self.logger.debug(f'{suspect.id} updated hitcount of listing {listing.list_id} via rest {endpoint} with response {response}')
            except RESTAPIError as e:
                self.logger.warning(f'{suspect.id} failed to update hitcount of listing {listing.list_id} via rest {endpoint} due to {str(e)}')

    def _update_hit_count(self, suspect: Suspect, listing: tp.Union[BlockWelcomeTable, BlockWelcomeEntry]):
        if isinstance(listing, BlockWelcomeTable):
            self._update_hit_count_sql(suspect, listing)
        elif isinstance(listing, BlockWelcomeEntry):
            self._update_hit_count_rest(suspect, listing)
        else:
            self.logger.warning(f'{suspect.id} invalid listing of type {type(listing)} data {listing}')

    def _test_listings(self, listings: tp.List[tp.Union[BlockWelcomeTable, BlockWelcomeEntry]]):
        errors = []
        for listing in listings:
            err = None
            if listing.list_type not in (BlockWelcomeEntry.TYPE_BLOCK, BlockWelcomeEntry.TYPE_WELCOME):
                err = f'invalid list_type {listing.list_type}'
            elif listing.list_scope not in (BlockWelcomeEntry.SCOPE_ANY, BlockWelcomeEntry.SCOPE_ENV, BlockWelcomeEntry.SCOPE_HDR):
                err = f'invalid list_scope {listing.list_scope}'
            elif not (
                    listing.scope == GLOBALSCOPE
                    or (listing.scope.startswith('%') and not '@' in listing.scope)
                    or not listing.scope.startswith('%') and '@' in listing.scope
            ):
                err = f'invalid scope {listing.scope}'
            elif listing.sender_addr is None and not listing.sender_host:
                err = 'no sender_addr and no sender_host'
            elif not (
                    listing.sender_addr in [None, '']
                    or (listing.sender_addr.startswith(('%', '*.')) and not '@' in listing.sender_addr)
                    or ('@' in listing.sender_addr and not listing.sender_addr.startswith(('%', '*.')))
            ):
                err = 'invalid sender_addr'
            elif not isinstance(listing.netmask, int):
                err = f'invalid netmask data type {type(listing.netmask)}'
            elif (
                    (not listing.sender_host and listing.netmask != -1)
                    or (listing.sender_host and listing.netmask == -1)
            ):
                err = f'invalid netmask {listing.netmask}'
            elif listing.sender_host:
                listing_net, listing_host = self._parse_host(listing)
                if listing.sender_host and listing_net is None and listing_host is None:
                    err = f'unparseable sender_host {listing.sender_host}'
                elif listing_host is not None and len(listing_host.split('.')) != listing.netmask:
                    err = f'mismatching sender_host {listing.sender_host} and netmask {listing.netmask}'
                elif listing_net and isinstance(listing_net, ipaddress.IPv4Address) and listing.netmask > 32:
                    err = f'illegal netmask {listing.netmask} for ipv4 sender_host'
                elif listing_net and isinstance(listing_net, ipaddress.IPv6Address) and listing.netmask > 128:
                    err = f'illegal netmask {listing.netmask} for ipv6 sender_host'

            if err is not None:
                errors.append((listing, err))
        return errors

    def lint(self):
        if not SQL_EXTENSION_ENABLED and self.config.get(self.section, 'fublwl_dbconnection'):
            print('WARNING: SQL extension not enabled but DB connection specified. This backend will not query SQLDB.')
        
        json_file = self.config.get(self.section, 'fublwl_json_file')
        if json_file:
            if not os.path.exists(json_file):
                print(f'ERROR: no such json file {json_file}')
                return False
            else:
                self._init_jsonfile()
                if self.jsonfile is None:
                    print(f'ERROR: failed to load json file {json_file}')
                    return False
                else:
                    entries = self.jsonfile.get_list()
                    if isinstance(entries, list):
                        print(f'ERROR: failed to parse json file {json_file}')
                        return False
        
        try:
            #dbtimeout=self.config.get('databaseconfig', 'restapi_timeout')
            #self.config.set('databaseconfig', 'restapi_timeout', '3')
            listings = self._get_listings()
            #self.config.set('databaseconfig', 'restapi_timeout', dbtimeout)
        except Exception as e:
            # for now, we do not let lint fail here to allow startup
            print(f'WARNING: failed to load listings due to {e.__class__.__name__}: {str(e)}')
            listings = {}
        else:
            if not listings:
                print('INFO: no listings loaded')
        #suspect = Suspect('sender@fuglu.org', 'recipient@fuglu.org', '/dev/null')
        #eval_order = self._get_eval_order(suspect, self.config.getlist(self.section, 'fublwl_eval_order', lower=True), have_global=True)
        #check_listings = self._sort_listings(suspect, listings, eval_order)
        # print(eval_order)
        # for listing in check_listings:
        #    print(str(listing))
        if listings:
            all_listings = []
            for scope in listings:
                #print(f'{scope} {[str(l) for l in listings[scope]]}')
                all_listings.extend(listings[scope])
            print('INFO: loaded %s listings' % len(all_listings))
            try:
                errors = self._test_listings(all_listings)
                for listing, err in errors:
                    print(f'{err} {str(listing)}')
                if errors:
                    return False
            except Exception as e:
                print(f'ERROR: failed to test listings due to {e.__class__.__name__}: {str(e)}')
                return False
        return True

    async def evaluate(self, suspect: Suspect, stage: str):
        if suspect.is_welcomelisted() or suspect.is_blocklisted():
            self.logger.debug(f'{suspect.id} Skip because already welcomelisted={suspect.is_welcomelisted()} blocklisted={suspect.is_blocklisted()}')
            return
        
        self._init_jsonfile()
        if not SQL_EXTENSION_ENABLED and not self.config.get(self.section, 'fublwl_restapi_endpoint') and not self.jsonfile:
            self.logger.debug(f"{suspect.id} Skip because SQL_EXTENSION is not enabled and fublwl_restapi is not set")
            return

        try:
            listings = self._get_listings(suspectid=suspect.id)
            self.logger.debug(f"{suspect.id} Checking {len(listings)} listings for {suspect.to_address}")
        except RESTAPIError as e:
            suspect.set_tag('restapi.error', e)
            return

        listing, list_scope = self._check_user_listings(suspect, listings, stage)
        self.logger.debug(f"{suspect.id} stage={stage} after applying {len(listings)} user listings -> listing: {listing}, list_scope: {list_scope}")

        if listing and listing.list_type == BlockWelcomeEntry.TYPE_BLOCK:
            self._add_tag(suspect, BLOCK)
        elif listing and listing.list_type == BlockWelcomeEntry.TYPE_WELCOME:
            self._add_tag(suspect, WELCOME)
            if listing.scope == GLOBALSCOPE:
                self._set_global_tag(suspect)
            if list_scope == BlockWelcomeEntry.SCOPE_HDR:
                suspect.set_tag('welcomelisted.header', True)
            elif list_scope == BlockWelcomeEntry.SCOPE_ENV and listing.sender_addr and listing.sender_host:
                suspect.set_tag('welcomelisted.confirmed', True)  # confirmed listings have both envelope sender address and sender host set
        
        if listing and self.config.getboolean(self.section, 'fublwl_update_hitcount') and not suspect.get_tag(f'hitcount-{listing.list_id}'):
            loop = get_event_loop()
            try:
                pool = suspect.pool # pool is passed to suspect in BlockWelcomeMilter._examine
            except AttributeError:
                self.logger.warning(f'{suspect.id} no pool specified')
                pool = None
            await loop.run_in_executor(pool, functools.partial(self._update_hit_count, suspect=suspect, listing=listing))
            suspect.set_tag(f'hitcount-{listing.list_id}', True)
        elif listing:
            previous = suspect.get_tag(f'hitcount-{listing.list_id}')
            self.logger.debug(f'{suspect.id} stage={stage} not updating hitcount for listing_id={listing.list_id} (set previously={previous})')
        
        if listing:
            suspect.set_tag('listing_id', listing.list_id)
            self.logger.info(f'{suspect.id} stage={stage} hits on listing {listing}')
        else:
            self.logger.info(f'{suspect.id} stage={stage} no listing hit')


class FilterSettingsBackend(AbstractBackend):
    """
    This backend reads specific values per recipient/recipient domain from fuglu database config and adds respective tags.
    allows global settings in config file or database.
    configure database configuration in [databaseconfig] section
    """

    requiredvars = {
        'fs_section_name': {
            'default': 'FilterSettings',
            'description': 'name of config section',
        },
        'fs_welcome_options': {
            'default': 'disable_filter',
            'description': 'options that act like "welcomelist_to" (boolean values only)',
        },
        'fs_yesno_options': {
            'default': 'deliver_spam, deliver_highspam, block_before_welcome, enforce_tls',
            'description': 'options that enable or disable a feature (boolean values only)',
        },
        'fs_level_options': {
            'default': 'subject_tag_ext_level, max_message_size',
            'description': 'options that set a level or threshold (numeric values only)',
        },
        'fs_value_options': {
            'default': 'spam_recipient, subject_tag_ext, subject_tag_spam, ca_target',
            'description': 'options that describe or configure other settings (text values, allows template variables like ${to_address})',
        },
        'fs_debug': {
            'default': 'False',
            'description': 'print debug output (extra verbose)',
        },

        'subject_tag_ext': {
            'section': 'FilterSettings',
            'default': '[EXTERNAL]',
            'description': 'default subject tag for tagging external messages',
        },
        'subject_tag_ext_level': {
            'section': 'FilterSettings',
            'default': '0',
            'description': 'when to tag external messages: 0 never, 1 always, 2 when sender domain equals recipient domain',
        },
        'subject_tag_spam': {
            'section': 'FilterSettings',
            'default': '[SPAM]',
            'description': 'default subject tag for tagging spam messages',
        },
        'spam_recipient': {
            'section': 'FilterSettings',
            'default': '${to_address}',
            'description': 'default subject tag for tagging spam messages',
        },
        'block_before_welcome': {
            'section': 'FilterSettings',
            'default': 'True',
            'description': 'evaluate blocklist before welcomelist (influences other backends/plugins)',
        },
    }

    def __init__(self, config, section):
        super().__init__(config, section)
        self.engine = 'FilterSettings'

    def _add_filtersetting_tag(self, suspect: Suspect, option: str, value: tp.Union[str, float, bool, tp.List[str]]):
        try:
            suspect.tags['filtersettings'][option] = value
        except KeyError:
            suspect.tags['filtersettings'] = {option: value}
        
        recipient = email_normalise_ebl(suspect.to_address)
        try:
            suspect.tags['miltersettings'][recipient][option] = value
        except KeyError:
            if not 'miltersettings' in suspect.tags:
                suspect.tags['miltersettings'] = {}
            if not recipient in suspect.tags['miltersettings']:
                suspect.tags['miltersettings'][recipient] = {option: value}
        

    async def evaluate(self, suspect: Suspect, stage: str):
        errors = set()
        dbsection = self.config.get(self.section, 'fs_section_name')
        debug = self.config.getboolean(self.section, 'fs_debug')

        runtimeconfig = DBConfig(self.config, suspect)
        loaded = runtimeconfig.load_section(self.section)  # maybe need to catch restapierror here
        if not loaded:
            self.logger.warning(f'{suspect.id} failed to load runtimeconfig, will proceed without cached data')

        welcome_options = self.config.getlist(self.section, 'fs_welcome_options', lower=True)
        for option in welcome_options:
            try:
                value = runtimeconfig.getboolean(dbsection, option)
                self._add_filtersetting_tag(suspect, option, value)
                if value:
                    self._add_tag(suspect, WELCOME)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                debug and self.logger.debug(f'{suspect.id} fs_welcome_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        yesno_options = self.config.getlist(self.section, 'fs_yesno_options', lower=True)
        for option in yesno_options:
            try:
                value = runtimeconfig.getboolean(dbsection, option)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                debug and self.logger.debug(f'{suspect.id} fs_yesno_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        level_options = self.config.getlist(self.section, 'fs_level_options', lower=True)
        for option in level_options:
            try:
                value = runtimeconfig.getfloat(dbsection, option)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                debug and self.logger.debug(f'{suspect.id} fs_level_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        value_options = self.config.getlist(self.section, 'fs_value_options', lower=True)
        for option in value_options:
            try:
                value = runtimeconfig.get(dbsection, option)
                value = apply_template(value, suspect)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                debug and self.logger.debug(f'{suspect.id} fs_value_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)
    
    
    
    async def lint(self):
        if not SQL_EXTENSION_ENABLED:
            print('WARNING: SQL extension not enabled, this backend will not read individual config overrides from databases')

        suspect = Suspect('sender@unittests.fuglu.org', 'recipient@unittests.fuglu.org', '/dev/null')
        await self.evaluate(suspect, 'lint')
        fs = suspect.tags.get('filtersettings')
        if fs:
            print('INFO:', fs)

        return True


class SAUserPrefBackend(AbstractBackend):
    """
    Backend that reads default SpamAssassin UserPref table
    """
    requiredvars = {
        'userpref_dbconnection': {
            'default': '',
            'description': "sqlalchemy db connect string, e.g. mysql:///localhost/spamassassin",
        },
        'userpref_usecache': {
            'default': "True",
            'description': 'Use Mem Cache. This is recommended. However, if enabled it will take up to userpref_cache_ttl seconds until listing changes are effective.',
        },
        'userpref_cache_ttl': {
            'default': "300",
            'description': 'how long to keep userpref data in memory cache',
        },
        'userpref_block_before_welcome': {
            'default': 'True',
            'description:': 'Does blocklist have precedence over welcome list',
        },
        'userpref_eval_order': {
            'default': 'user,domain,global',
            'description:': 'in which order to evaluate [global, domain, user] listings. defaults to user before domain before global',
        },
    }

    USERPREF_TYPES = OrderedDict()
    USERPREF_TYPES['whitelist_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['welcomelist_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['more_spam_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['all_spam_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['whitelist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': WELCOME}
    USERPREF_TYPES['welcomelist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': WELCOME}
    USERPREF_TYPES['blacklist_to'] = {'cmp': ['to_address'], 'act': BLOCK}
    USERPREF_TYPES['blocklist_to'] = {'cmp': ['to_address'], 'act': BLOCK}
    USERPREF_TYPES['blacklist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': BLOCK}
    USERPREF_TYPES['blocklist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': BLOCK}

    def __init__(self, config, section):
        super().__init__(config, section)
        self.cache = get_default_cache()
        self.engine = 'UserPref'

    def __str(self):
        return 'UserPref'

    def lint(self):
        if not SQL_EXTENSION_ENABLED:
            print('WARNING: SQL extension not enabled, this backend will do nothing')

        suspect = Suspect('dummy@example.com', 'dummy@example.com', '/dev/null')
        if not self.config.get(self.section, 'userpref_dbconnection'):
            print('WARNING: spamassassin userprefs enabled but no db connection configured')
            return False
        else:
            try:
                listings = self._get_sa_userpref()
                print('INFO: retrieved %s global/dummy userprefs' % len(listings))
                self._check_sa_userpref(suspect, listings)
            except Exception as e:
                print(f'ERROR: failed to retrieve spamassassin userpref due to {e.__class__.__name__}: {str(e)}')
                return False
        return True

    def _get_sa_userpref(self):
        key = 'blwl-userpref'
        usecache = self.config.getboolean(self.section, 'userpref_usecache')
        listings = OrderedDict()
        if usecache:
            listings = self.cache.get_cache(key) or OrderedDict()
        if not listings:
            dbconn = self.config.get(self.section, 'userpref_dbconnection')
            if not dbconn:
                self.logger.debug('userpref_dbconnection not set')
                return listings

            dbsession = get_session(dbconn)
            query = dbsession.query(UserPref)
            query = query.filter(UserPref.preference.in_(list(self.USERPREF_TYPES.keys())))
            query = query.order_by(desc(UserPref.username))
            result = query.all()
            for r in result:
                listing_type = r.preference
                if not listing_type in listings:
                    listings[listing_type] = {}
                username = r.username
                if username.startswith('*@'):  # roundcube sauserprefs plugin domain wide scope
                    username = username.lstrip('*@')
                    username = f'%{username}'
                try:
                    listings[listing_type][username].append(r.value)
                except KeyError:
                    listings[listing_type][username] = [r.value]
            if listings:
                cachettl = self.config.getint(self.section, 'userpref_cache_ttl')
                self.cache.put_cache(key, listings, ttl=cachettl)
        return listings

    def _compare_sa_userpref(self, listings, listtype, user, value):
        if not listings:
            return False

        try:
            userlistings = listings[listtype].get(user, [])
        except KeyError:
            return False

        for l in userlistings:
            if fnmatch.fnmatch(value, l):
                listed = True
                break
        else:
            listed = False
        return listed

    def _get_pref_order(self, suspect: Suspect, listings):
        block_before_welcome = self._get_filtersetting(suspect, 'block_before_welcome', True)
        if block_before_welcome:
            return list(listings.keys())
        else:
            return reversed(list(listings.keys()))

    def _check_sa_userpref(self, suspect: Suspect, listings):
        if not listings:
            return

        items = [i.lower() for i in self.config.getlist(self.section, 'userpref_eval_order')]
        eval_order = self._get_eval_order(suspect, items, have_global=True)
        pref_order = self._get_pref_order(suspect, listings)

        for preference in pref_order:
            check = self.USERPREF_TYPES[preference]
            act = check['act']
            for cmp in check['cmp']:
                cmp_value = getattr(suspect, cmp)
                for scope in eval_order:
                    listed = self._compare_sa_userpref(listings, preference, scope, cmp_value)
                    if listed:
                        blocktype = 'block' if act == WELCOME else 'welcome'
                        self.logger.debug(f'{suspect.id} userpref hit pref={preference} scope={scope} val={cmp_value} type={blocktype}')
                        if scope == GLOBALSCOPE and act == WELCOME:
                            self._set_global_tag(suspect)
                        elif act == BLOCK:
                            suspect.set_tag('blocklisted.preference', preference)
                            suspect.set_tag('blocklisted.scope', scope)
                            suspect.set_tag('blocklisted.value', cmp_value)
                        return act
        return None

    async def evaluate(self, suspect: Suspect, stage: str):
        if not SQL_EXTENSION_ENABLED:
            return

        try:
            listings = self._get_sa_userpref()
        except Exception as e:
            listings = None
            self.logger.error(f'{suspect.id} failed to retrieve userprefs due to {e.__class__.__name__}: {str(e)}')

        action = self._check_sa_userpref(suspect, listings)
        self._add_tag(suspect, action)


class StaticBackend(AbstractBackend):
    """
    Backend for statically defined listings
    """
    requiredvars = {
        'static_recipients_welcome': {
            'default': '',
            'description': "list of recipients that to which all mail is supposed to be welcome",
        },
        'static_senders_welcome': {
            'default': '',
            'description': "list of senders that are always welcomelisted (domains or full addresses)",
        },
        'static_senders_blocked': {
            'default': '',
            'description': "list of senders that are always blocked (domains or full addresses)",
        },
    }
    engine = 'Static'

    async def evaluate(self, suspect: Suspect, stage: str):
        if not stage in [asm.RCPT, STAGE_PREPENDER]:
            self.logger.debug(f'{suspect.id} backend={self.engine} skipped in stage={stage}')
            return

        recipients_welcome = self.config.getlist(self.section, 'static_recipients_welcome')
        for recipient in suspect.recipients:
            if recipient in recipients_welcome or recipient.rsplit('@', 1)[-1] in recipients_welcome:
                self.logger.info(f'{suspect.id} is welcome (rcpt={recipient})')
                self._add_tag(suspect, WELCOME)
                self._set_global_tag(suspect)
                break
        else:
            if recipients_welcome:
                self.logger.debug(f'{suspect.id} no rcpt in {",".join(suspect.recipients)} is in recipients welcome list {",".join(recipients_welcome)}')

        senders_welcome = self.config.getlist(self.section, 'static_senders_welcome')
        if suspect.from_address in senders_welcome or suspect.from_domain in senders_welcome:
            self.logger.info(f'{suspect.id} is welcome (sender={suspect.from_address or "<>"})')
            self._add_tag(suspect, WELCOME)
            self._set_global_tag(suspect)
        elif senders_welcome:
            self.logger.debug(f'{suspect.id} {suspect.from_address or "<>"} is not in senders welcome list {",".join(senders_welcome)}')

        senders_blocked = self.config.getlist(self.section, 'static_senders_blocked')
        if suspect.from_address in senders_blocked or suspect.from_domain in senders_blocked:
            self.logger.info(f'{suspect.id} is blocked')
            self._add_tag(suspect, BLOCK)
        elif senders_blocked:
            self.logger.debug(f'{suspect.id} {suspect.from_address or "<>"} is not in senders blocked list {",".join(senders_blocked)}')

    def lint(self):
        return True


class AutoListMixin(object):
    config = None
    section = None
    requiredvars = {
        'al_redis_conn': {
            'default': 'redis://127.0.0.1:6379/1',
            'description': 'the redis database connection URI: redis://host:port/dbid',
        },
        'al_redis_ttl': {
            'default': str(7 * 24 * 3600),
            'description': 'TTL in seconds',
        },
        'al_redis_timeout': {
            'default': '2',
            'description': 'redis timeout in seconds'
        },
        'al_skip_headers': {
            'default': '',
            'description': 'list of headers which disable autolist if header is found',
        },
        'al_max_count': {
            'default': '1000',
            'description': 'do not increase counter beyond this value (for performance reasons)'
        },
        'al_header_as_env_sender': {
            'default': '',
            'description': 'override envelope sender with value from one of these headers (if set - first occurrence wins)'
        },
        'al_header_as_env_recipient': {
            'default': '',
            'description': 'override envelope recipient with value from one of these headers (if set - first occurrence wins)'
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend_redis = None
        self._aioredisbackend = None
        
    def _get_env_override(self, suspect: Suspect, env_headers) -> tp.Union[None, str]:
        for header in env_headers:
            value = suspect.get_header(header)
            if value and '@' in value:
                return value
        return None

    def _envelope_skip(self, envelope_sender: str, envelope_recipient: str):
        if envelope_recipient is None or envelope_sender is None or envelope_sender == envelope_recipient:
            return True
        if envelope_sender in ['', '<>'] or envelope_recipient == '' or not is_email(envelope_sender or not is_email(envelope_recipient)):
            return True
        return False

    def _header_skip(self, suspect: Suspect):
        """Check if evaluation should be skipped due to header in skiplist"""
        try:
            headers_list = self.config.getlist(self.section, 'al_skip_headers')
            msrep = suspect.get_message_rep()
            for h in headers_list:
                if msrep.get(h, None):
                    return h
        except Exception:
            pass
        return None
    
    @property
    def aioredisbackend(self) -> AIORedisBaseBackend:
        if self._aioredisbackend is None:
            redis_url = self.config.get(self.section, 'al_redis_conn')
            self._aioredisbackend = AIORedisBaseBackend(redis_url=redis_url, logger=self.logger)
        return self._aioredisbackend

    def _init_backend_redis(self):
        """
        Init Redis backend if not yet setup.
        """
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'al_redis_conn')
        if redis_conn:
            ttl = self.config.getint(self.section, 'al_redis_ttl')
            maxcount = self.config.getint(self.section, 'al_max_count')
            timeout = self.config.getint(self.section, 'al_redis_timeout')
            self.backend_redis = ExpiringCounter(self.aioredisbackend, ttl, maxcount=maxcount, timeout=timeout)

    def _address_normalise(self, address: str) -> str:
        if DOMAINMAGIC_AVAILABLE and address:
            return strip_batv(email_normalise_ebl(force_uString(address)))
        else:
            return address.lower()

    def _gen_key(self, sender: str, recipient: str) -> str:
        # rcpt first to allow more efficient search by rcpt
        return f'{recipient}\n{sender}'

    async def lint(self):
        if not DOMAINMAGIC_AVAILABLE:
            print('WARNING: domainmagic not available')

        if not REDIS_AVAILABLE:
            print('ERROR: redis not available')
            return False

        ok = True
        try:
            reply = await self.aioredisbackend.ping()
            if reply:
                print("OK: redis server replied to ping")
            else:
                ok = False
                print("ERROR: redis server did not reply to ping")
        except Exception as e:
            ok = False
            print(f"ERROR: failed to connect to redis: {e.__class__.__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
        return ok


class AutoListBackend(AbstractBackend, AutoListMixin):
    """
    Welcomelist Backend for Autolist (sender/recipient pairs with frequent communication)
    """
    requiredvars = {
        'al_threshold': {
            'default': '50',
            'description': 'threshold for auto welcomelisting. Set to 0 to never welcomelist.',
        },
        'al_sa_headername': {
            'default': 'X-AutoWL-Lvl',
            'description': 'header name for SpamAssassin',
        },
    }
    requiredvars.update(AutoListMixin.requiredvars)

    def __init__(self, config, section):
        super().__init__(config, section)
        AutoListMixin.__init__(self)
        self.engine = 'AutoList'

    async def evaluate(self, suspect: Suspect, stage: str):
        if not REDIS_AVAILABLE:
            return
        if not stage in [asm.RCPT, STAGE_PREPENDER]:
            self.logger.debug(f'{suspect.id} backend={self.engine} skipped in stage={stage}')
            return
        if suspect.is_welcomelisted() or suspect.is_blocklisted():
            self.logger.debug(f'{suspect.id} backend={self.engine} skipped because welcome={suspect.is_welcomelisted()} block={suspect.is_blocklisted()}')
            return
        
        env_headers = self.config.getlist(self.section, 'al_header_as_env_sender')
        if env_headers:
            envelope_sender = self._address_normalise(self._get_env_override(suspect, env_headers) or '')
        else:
            envelope_sender = self._address_normalise(suspect.from_address)
            
        env_headers = self.config.getlist(self.section, 'al_header_as_env_recipient')
        if env_headers:
            envelope_recipient = self._address_normalise(self._get_env_override(suspect, env_headers) or '')
        else:
            envelope_recipient = self._address_normalise(suspect.to_address)
        
        if self._envelope_skip(envelope_sender, envelope_recipient):
            self.logger.info(f'{suspect.id} backend={self.engine} skipped due to envelope sender={envelope_sender} recipient={envelope_recipient}')
            return
        header = self._header_skip(suspect)
        if header:
            self.logger.info(f'{suspect.id} backend={self.engine} skipped due to header {header}')
            return

        rediskey = self._gen_key(envelope_sender, envelope_recipient)
        count = await self._get_count(suspect, rediskey)
        if count < 0: # error querying redis
            return
        
        welcome = False
        threshold = self.config.getint(self.section, 'al_threshold')
        if count is not None and count > 0:
            if count > threshold > 0:
                self._add_tag(suspect, WELCOME)
                welcome = True
            headername = self.config.get(self.section, 'al_sa_headername')
            if headername:
                suspect.write_sa_temp_header(headername, str(count))
        else:
            count = 0
        suspect.set_tag('autolist.score', count)
        self.logger.info(f'{suspect.id} autolist: mail from={envelope_sender} to={envelope_recipient} seen={count} threshold={threshold} welcome={welcome}')
    
    
    async def _get_count(self, suspect:Suspect, rediskey:str) -> int:
        count = -1
        self._init_backend_redis()
        if self.backend_redis:
            count = await self.backend_redis.get_count(rediskey)
            if count == -1:
                self.logger.warning(f'{suspect.id} failed to retrieve autolist data for {rediskey}')
        return count
    
    async def _reset(self, rediskey: str):
        self._init_backend_redis()
        val = await self.backend_redis.reset(rediskey)
        return val
    
    async def lint(self):
        return await AutoListMixin.lint(self)


class RBLBackend(AbstractBackend):
    """
    Welcomelist Backend for Autolist (sender/recipient pairs with frequent communication)
    """
    requiredvars = {
        
            'rbl_blocklistconfig': {
                'default': '${confdir}/rblblwl.conf',
                'description': 'Domainmagic RBL lookup config file',
            },
            'rbl_welcomelists': {
                'default': '',
                'description': 'which RBL identifiers are welcome list entries? hint: add those on top of your rbl.conf',
            },
    }
    requiredvars.update(AutoListMixin.requiredvars)

    def __init__(self, config, section):
        super().__init__(config, section)
        self.rbllookup = None
        self.engine = 'RBL'

    def _init_rbllookup(self):
        if self.rbllookup is None:
            blocklistconfig = self.config.get(self.section, 'rbl_blocklistconfig')
            
            if not blocklistconfig:
                self.logger.error('blocklistconfig not set in config')
            elif not os.path.exists(blocklistconfig):
                self.logger.error(f'blocklistconfig file {blocklistconfig} does not exist')
            
            if blocklistconfig and os.path.exists(blocklistconfig):
                self.rbllookup = RBLLookup()
                self.rbllookup.from_config(blocklistconfig)

    async def evaluate(self, suspect: Suspect, stage: str):
        if not DOMAINMAGIC_AVAILABLE:
            self.logger.debug(f'{suspect.id} No action - Domainmagic not available')
            return
        
        if not suspect.from_domain:
            self.logger.debug(f'{suspect.id} No action - bounce')
            return
        
        self._init_rbllookup()
        if self.rbllookup is None:
            self.logger.error(f'{suspect.id} No action - blocklistconfig could not be loaded')
            return
        
        welcomelists = self.config.getlist(self.section, 'rbl_welcomelists')
        listings = self.rbllookup.listings(suspect.from_domain)
        for identifier, humanreadable in iter(listings.items()):
            if identifier in welcomelists:
                self.logger.info(f'{suspect.id} {suspect.from_domain} welcomelisted by {identifier}')
                self._add_tag(suspect, WELCOME)
                self._set_global_tag(suspect)
                break
            else:
                self.logger.info(f'{suspect.id} {suspect.from_domain} blocklisted by {identifier}')
                self._add_tag(suspect, BLOCK)
                break
        else:
            self.logger.debug(f'{suspect.id} {suspect.from_domain} not listed in any RBL')
    
    def lint(self):
        if not DOMAINMAGIC_AVAILABLE:
            print('ERROR: domainmagic not available for RBL')
            return False
        self._init_rbllookup()
        if self.rbllookup is None:
            print('ERROR: blocklistconfig could not be loaded for RBL')
            return False
        welcomelists = self.config.getlist(self.section, 'rbl_welcomelists')
        print(f'INFO: defined welcomelists: {", ".join(welcomelists)} for RBL')
        return True


BLWL_BACKENDS = OrderedDict()
BLWL_BACKENDS['fublwl'] = FugluBlockWelcome
BLWL_BACKENDS['filtersettings'] = FilterSettingsBackend
BLWL_BACKENDS['userpref'] = SAUserPrefBackend
BLWL_BACKENDS['static'] = StaticBackend
BLWL_BACKENDS['autolist'] = AutoListBackend
BLWL_BACKENDS['rbl'] = RBLBackend


class BlockWelcomeList(PrependerPlugin):
    """
    This plugin evaluates block and welcome lists, e.g. from spamassassin userprefs.
    Respective tags if a sender/recipient combination is welcome listed or block listed are written.
    use e.g. p_skipper.PluginSkipper to skip certain checks, see decision.FilterDecision for possible uses, or create a custom plugin to decide further action

    Check p_blwl.py module code for available backends and their respective config options
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.backends = None
        self.filter = None
        self.requiredvars = {
            'blwl_backends': {
                'default': '',
                'description': 'comma separated list of backends to use. available backends: %s' % ', '.join(list(BLWL_BACKENDS.keys())),
            },
            'skipfile': {
                'default': '',
                'description':  """Skip following backends if a certain SuspectFilter criteria is met
                                @tagname    value   backendname
                                """,
            },
        }
        for backend_name in BLWL_BACKENDS:
            self.requiredvars.update(BLWL_BACKENDS[backend_name].requiredvars)

    def __str__(self):
        return "Block and welcome list evaluation plugin"

    def _load_backends(self):
        self.backends = OrderedDict()
        backend_names = self.config.getlist(self.section, 'blwl_backends')
        for backend_name in backend_names:
            try:
                backendclass = BLWL_BACKENDS[backend_name]
                backend = backendclass(self.config, self.section)
                self.backends[backend_name] = backend
            except KeyError:
                self.logger.error(f'invalid backend name {backend_name}')

    def _initfilter(self):
        if self.filter is not None:
            return True

        filename = self.config.get(self.section, 'skipfile')
        if filename is None or filename == "":
            return False

        if not os.path.exists(filename):
            self.logger.error(f'Skipfile not found: {filename}')
            return False

        self.filter = SuspectFilter(filename)
        return True

    def _skip_backend(self, suspect: Suspect, backendname) -> bool:
        if not self._initfilter():
            return False
        match, backends = self.filter.matches(suspect)
        if match:
            backendlist = [b.strip() for b in backends.split(',')]
            if backendname in backendlist:
                return True
        return False

    async def _run_backends(self, suspect: Suspect, stage: str):
        if self.backends is None:
            self._load_backends()
        self.logger.debug(f"{suspect.id} stage={stage} available backends: {', '.join(list(self.backends.keys()))}")
        for backend_name in self.backends:
            if self._skip_backend(suspect, backend_name):
                self.logger.debug(f"{suspect.id} stage={stage} skipping backend: {backend_name}")
                continue
            self.logger.debug(f"{suspect.id} stage={stage} evaluating backend: {backend_name}")
            backend = self.backends[backend_name]
            try:
                await backend.evaluate(suspect, stage)
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)
            except Exception as e:
                self.logger.debug(traceback.format_exc())
                self.logger.error(f'{suspect.id} stage={stage} backend {backend_name} failed to evaluate due to {e.__class__.__name__}: {str(e)}')

    async def pluginlist(self, suspect: Suspect, pluginlist):
        await self._run_backends(suspect, STAGE_PREPENDER)
        return pluginlist

    async def lint(self):
        ok = self.check_config()
        if ok:
            self._load_backends()
            print('loaded backends: %s' % ', '.join(self.backends.keys()))
            for backend_name in self.backends:
                backend = self.backends[backend_name]
                if asyncio.iscoroutinefunction(backend.lint):
                    backend_ok = await backend.lint()
                else:
                    backend_ok = backend.lint()
                if not backend_ok:
                    ok = False
        return ok


class BlockWelcomeMilter(BMPRCPTMixin, BMPEOHMixin, BasicMilterPlugin, BlockWelcomeList):
    """
    Milter Plugin to evaluate block and welcome listings based on sender, sender server and recipient.

    Supports various backends for different listing sources and rule sets.

    Upon welcomelisting hit, mail is marked accordingly in tags. It is also possible to ACCEPT instantly.

    Upon blocklisting, mail is marked or rejected.

    Check p_blwl.py module code for available backends and their respective config options
    """

    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        BlockWelcomeList.__init__(self, config, section)
        self.logger = self._logger()

        requiredvars = {
            'welcomeaction': {
                'default': 'DUNNO',
                'description': "default action on welcome list hit (usually DUNNO or ACCEPT - ACCEPT will end milter processing)",
            },

            'blockaction': {
                'default': 'REJECT',
                'description': "default action on block list hit (usually REJECT)",
            },

            'rejectmessage': {
                'default': 'message identified as spam',
                'description': "reject message template if running in milter mode",
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied {asm.RCPT}, {asm.EOH}'
            },

            'wltagname': {
                'default': 'skipmplugins',
                'description': 'tagname in case of WL hit (empty: don\'t set, skipmplugins to skip milter plugins)'
            },

            'wltagvalue': {
                'default': '',
                'description': 'tag content in case of WL hit (empty: don\'t set)'
            },
        }
        self.requiredvars.update(requiredvars)

    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return await self._examine(sess, recipient, stage=asm.RCPT)

    async def examine_eoh(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return await self._examine(sess, sess.to_address, stage=asm.EOH)

    async def _examine(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes, stage: str) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        self.logger.debug(f"{sess.id} -> examine with recipient: {force_uString(recipient)}")
        pseudobody = b''
        for hdr, val in sess.original_headers:
            pseudobody += hdr + b': ' + val + b'\r\n'
        pseudobody += b'\r\n\r\n'

        suspect = Suspect(force_uString(sess.sender), force_uString(recipient), None, id=sess.id,
                          queue_id=sess.queueid, milter_macros=sess.milter_macros, inbuffer=pseudobody)
        suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.ptr)
        suspect.timestamp = sess.timestamp
        suspect.tags = sess.tags  # pass by reference - any tag change in suspect should be reflected in session
        suspect.pool = sess.mhandler.pool # pass sess pool for async calls
        #suspect.source = b''
        # for hdr, val in sess.original_headers:
        #    suspect.add_header(hdr, val, True)
        self.logger.debug(f"{sess.id} initialised temp suspect in stage={stage} with body={len(pseudobody)}b and source={len(suspect.get_source())}")
        stageaction = DUNNO
        message = None
        try:
            await self._run_backends(suspect, stage)
            if suspect.is_blocklisted():
                stageaction = string_to_actioncode(self.config.get(self.section, 'blockaction'), self.config)
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect)
            elif suspect.is_welcomelisted():
                stageaction = string_to_actioncode(self.config.get(self.section, 'welcomeaction'), self.config)

                wltag = self.config.get(self.section, 'wltagvalue')
                wlname = self.config.get(self.section, 'wltagname')
                if wlname and wltag:
                    self.logger.info(f"{sess.id} -> welcomelisting, tags defined, skip -> {wlname}:{wltag}")
                    stageaction = DUNNO
                    if wlname in sess.tags:
                        sess.tags[wlname] = f"{sess.tags[wlname]},{wltag}"
                    else:
                        sess.tags[wlname] = wltag
        except RESTAPIError:
            stageaction = DEFER
            message = 'Internal Server Error'

        return convert_return2milter((stageaction, message))


class IncrementOverridesLoader(FileList, AutoListMixin):
    def _parse_lines(self, lines):
        incrementsdict = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    user, incr = line.rsplit(':',1)
                    user = user.strip().lower()
                    if '@' in user:
                        user = self._address_normalise(user)
                    incr = int(incr.strip())
                    incrementsdict[user] = incr
                except ValueError as e:
                    self.logger.error(f'invalid line: {line} due to {str(e)}')
        return incrementsdict


class AutoListAppender(AppenderPlugin, AutoListMixin):
    """
    Learn known sender/recipient pairs to redis database. Training plugin for AutoList Backend of BlockWelcome Plugin
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        AutoListMixin.__init__(self)
        self.logger = self._logger()

        self.requiredvars = {
            'max_sa_score': {
                'default': '3',
                'description': 'do not count mail with SpamAssassin score higher than this'
            },
            'increment': {
                'default': '1',
                'description': 'increase counter by this value',
            },
            'increment_trusted': {
                'default': '10',
                'description': 'increase counter by this value for "outbound" mail',
            },
            'increment_overrides': {
                'default': '',
                'description': 'path to file with increment overrides. one override per line, format is user:val or domain:val',
            },
            'trustedport': {
                'default': '10099',
                'description': 'messages incoming on this port will be considered to be "outbound"',
            },
        }
        self.requiredvars.update(AutoListMixin.requiredvars)
        self.engine = 'AutoList'
        self.increment_overrides = None
        self._aioredisbackend = None
        
    def _init_increments(self):
        if self.increment_overrides is None:
            filepath = self.config.get(self.section, 'increment_overrides')
            if filepath and os.path.exists(filepath):
                self.increment_overrides = IncrementOverridesLoader(filename=filepath)
            elif filepath:
                self.logger.error(f'not setting increment_overrides, file {filepath} not found')
    
    def _get_increment(self, suspect: Suspect, user:str, is_trusted:bool) -> int:
        increment = None
        
        self._init_increments()
        if self.increment_overrides:
            increment_overrides = self.increment_overrides.get_list()
            increment = increment_overrides.get(user)
            if increment is None:
                increment = increment_overrides.get(user.rsplit('@',1)[-1])
            if increment is not None:
                self.logger.debug(f'{suspect.id} got increment override value of {increment} for {user}')
        
        if increment is None:
            if is_trusted:
                increment = self.config.getint(self.section, 'increment_trusted')
            else:
                increment = self.config.getint(self.section, 'increment')
        return increment
    
    def _get_spamscore(self, suspect: Suspect) -> float:
        spamscore = suspect.get_tag('SpamAssassin.score')
        if spamscore is None or suspect.get_tag('SpamAssassin.skipreason') is not None:
            score = 0
        else:
            try:
                score = float(spamscore)
            except ValueError:
                score = 5
        return score
    
    def _get_sender(self, suspect: Suspect, is_trusted: bool) -> str:
        env_headers = self.config.getlist(self.section, 'al_header_as_env_sender')
        if env_headers:
            sender = self._address_normalise(self._get_env_override(suspect, env_headers) or '')
        else:
            sender = self._address_normalise(suspect.from_address) # use envelope sender
        sender_domain = sender.rsplit('@', 1)[-1]
        if is_trusted:
            for header in ['reply-to', 'from']:  # also add from and reply-to header address if mail is trusted (outbound)
                header_from = suspect.parse_from_type_header(header=header)
                if header_from and header_from[0] and header_from[0][1]:
                    header_from_address = self._address_normalise(header_from[0][1])
                    header_from_domain = header_from_address.rsplit('@', 1)[-1]
                    if sender == header_from_address:
                        #self.logger.debug(f'{suspect.id} envelope sender {sender} identical to header {header} address {header_from_address}')
                        break
                    elif sender_domain == header_from_domain:
                        self.logger.debug(f'{suspect.id} overriding envelope sender {sender} with header {header} address {header_from_address}')
                        sender = header_from_address
                        break
                    else:
                        self.logger.debug(f'{suspect.id} not overriding envelope sender {sender} with header {header} address {header_from_address} - domain mismatch')
        return sender
    
    
    async def process(self, suspect: Suspect, decision):
        if not REDIS_AVAILABLE:
            return

        if not suspect.is_ham():
            self.logger.debug(f'{suspect.id} Skipped non ham message')
            return
        
        if suspect.is_welcomelisted() and self.engine not in suspect.tags['welcomelisted']:
            self.logger.debug(f'{suspect.id} Skipped welcomelisted message')
            return

        header = self._header_skip(suspect)
        if header:
            self.logger.debug(f'{suspect.id} Skipped due to header {header}')
            return

        sascore = self._get_spamscore(suspect)
        if sascore > self.config.getfloat(self.section, 'max_sa_score'):
            self.logger.debug(f'{suspect.id} Skipped due to spam score {sascore}')
            return
        
        await self._update_data(suspect, sascore)
        
        
    async def _update_data(self, suspect, sascore):
        is_trusted = self.config.getint(self.section, 'trustedport') == suspect.get_tag('incomingport')
        self.logger.debug(f"{suspect.id} mail received on {'' if is_trusted else 'non-'}trusted port {suspect.get_tag('incomingport')} with sascore {sascore}")
        sender = self._get_sender(suspect, is_trusted)
        
        for recipient in suspect.recipients:
            envelope_recipient = self._address_normalise(recipient)

            if self._envelope_skip(sender, envelope_recipient):
                self.logger.debug(f'{suspect.id} Skipped due to sender={sender} recipient={envelope_recipient}')
                continue

            if is_trusted:
                rediskey = self._gen_key(envelope_recipient, sender)
                increment = self._get_increment(suspect, sender, is_trusted)
            else:
                rediskey = self._gen_key(sender, envelope_recipient)
                increment = self._get_increment(suspect, envelope_recipient, is_trusted)
            
            if increment > 0:
                await self._store_redis(suspect, rediskey, increment)
            else:
                self.logger.debug(f'{suspect.id} Skipped due to sender={sender} recipient={envelope_recipient} increment={increment}')
    
    
    async def _store_redis(self, suspect, rediskey, increment):
        self._init_backend_redis()
        if self.backend_redis:
            result = await self.backend_redis.increase(rediskey, increment)
            if result == 0:
                self.logger.error(f'{suspect.id} failed to register autolist {rediskey} due to TimeoutError in backend (result==0)')
            else:
                self.logger.debug(f"{suspect.id} autolist {rediskey} registered with result {result}")
    
    
    async def lint(self):
        ok = await AutoListMixin.lint(self)
        self._init_increments()
        if ok and self.increment_overrides is None:
            filename = self.config.get(self.section, 'increment_overrides')
            if filename:
                print(f'ERROR: failed to load increment_overrides file {filename} exists={os.path.exists(filename)}')
                ok = False
        elif ok and self.increment_overrides:
            overrides = self.increment_overrides.get_list()
            print(f'INFO: found {len(overrides)} increment_overrides')
        return ok


