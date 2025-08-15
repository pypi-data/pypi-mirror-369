#!/usr/bin/python
# -*- coding: UTF-8 -*-
#   Copyright 2012-2022 Fumail Project
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
import configparser
import sys
# in case the tool is not installed system wide (development...)
if __name__ == '__main__':
    sys.path.append('../../')

import smtplib
from string import Template
import logging
import datetime
import os
import re
import time
import threading
import typing as tp
import ssl
import ipaddress
import socket
import asyncio
from urllib.parse import urlparse

try:
    import socks
    HAVE_PYSOCKS = True
except ImportError:
    class socks:
        HTTP = None
        SOCKS4 = None
        SOCKS5 = None
    HAVE_PYSOCKS = False

try:
    from domainmagic.mailaddr import strip_batv
    HAVE_DOMAINMAGIC = True
except ImportError:
    def strip_batv(value):
        return value
    HAVE_DOMAINMAGIC = False

import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
from fuglu.shared import _SuspectTemplate, Cache, FuConfigParser, FileList, get_outgoing_helo, utcnow, \
    Suspect, ScannerPlugin, DUNNO, string_to_actioncode, SuspectFilter
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DBConfig, RESTAPIError, text, sql_alchemy_version, SQL_ALCHEMY_V1, SQL_ALCHEMY_V2, DeclarativeBase
import fuglu.extensions.aiodnsquery as aiodnsquery
from fuglu.extensions.aioredisext import AIORedisBaseBackend, ENABLED as REDIS_ENABLED
from fuglu.scansession import TrackTimings
from fuglu.asyncprocpool import get_event_loop

if SQL_EXTENSION_ENABLED:
    from sqlalchemy.sql.expression import or_
    from sqlalchemy import Column, UniqueConstraint
    from sqlalchemy.types import Unicode, Integer, TIMESTAMP, Boolean


def get_config(fugluconfigfile=None, dconfdir=None):
    newconfig = FuConfigParser()
    logger = logging.getLogger('fuglu.plugin.ca.get_config')

    if fugluconfigfile is None:
        fugluconfigfile = '/etc/fuglu/fuglu.conf'

    if dconfdir is None:
        dconfdir = '/etc/fuglu/conf.d'

    with open(fugluconfigfile) as fp:
        newconfig.read_file(fp)

    # load conf.d
    if os.path.isdir(dconfdir):
        filelist = os.listdir(dconfdir)
        configfiles = [dconfdir + '/' + c for c in filelist if c.endswith('.conf')]
        logger.debug(f'Conffiles in {dconfdir}: {configfiles}')
        readfiles = newconfig.read(configfiles)
        logger.debug(f'Read additional files: {readfiles}')
    return newconfig


class BackendMixin:
    config = None
    section = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = None
        self.config_backend = None

    def _init_cache(self, config=None, section=None):
        if config is None:
            config = self.config
        if section is None:
            section = self.section
        if self.cache is None:
            try:
                storage = config.get(section, 'cache_storage')
            except (configparser.NoSectionError, configparser.NoOptionError):
                logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
                logger.error(f'config error: no section {section} or no option cache_storage in {section} - using memory')
                storage = 'memory'
            if storage == 'sql':
                self.cache = MySQLCache(config, section)
            elif storage == 'redis':
                self.cache = RedisCache(config, section)
            elif storage == 'memory':
                self.cache = MemoryCache(config, section)

    def _init_config_backend(self, recipient, config=None, section=None, sess=None):
        if config is None:
            config = self.config
        if section is None:
            section = self.section
        try:
            backend = config.get(section, 'config_backend')
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
            logger.error(f'config error: no section {section} or no option config_backend in {section}')
            backend = None
        if self.config_backend is None:
            if backend == 'sql':
                self.config_backend = MySQLConfigBackend(config, section)
            elif backend == 'dbconfig':
                self.config_backend = DBConfigBackend(config, section)
            elif backend == 'file':
                self.config_backend = ConfigFileBackend(config, section)
            elif backend and backend.startswith('tag:'):
                self.config_backend = TagConfigBackend(config, section)
            else:
                self.config_backend = ConfigBackendInterface(config, section)
                self.config_backend.logger.error(f'unknown config backend {self.config_backend}')
        if backend and backend.startswith('tag:'):
            self.config_backend.set_sess(sess, backend)
        self.config_backend.set_rcpt(recipient)


class AddressCheck(BackendMixin, BMPRCPTMixin, BasicMilterPlugin):
    """
    Flexibly query if a recipient exists on target server.
    Query result is cached in a global database (sql or redis).
    To reliably determine existing recipients, the target server must support recipient filtering and give a proper
    SMTP response after RCPT TO. 2xx for existing users, 5xx for non-existing users.
    To determine recipient filtering availability we test against a "random" user. If such user is accepted
    the target server is added to a skiplist.

    Config Backend SQL:
CREATE TABLE `ca_configoverride` (
  `domain` varchar(255) NOT NULL,
  `confkey` varchar(255) NOT NULL,
  `confvalue` varchar(255) NOT NULL,
  PRIMARY KEY (`domain`,`confkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    SQL Cache storage:
CREATE TABLE `ca_skiplist` (
  `relay` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `check_ts` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expiry_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `check_stage` varchar(20) DEFAULT NULL,
  `reason` varchar(400) DEFAULT NULL,
  PRIMARY KEY (`relay`,`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ca_addresscache` (
  `email` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `check_ts` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expiry_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `positive` tinyint(1) NOT NULL,
  `message` text DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.relaycache = Cache()
        self.enabletimetracker = False

        self.requiredvars = {
            'cache_storage': {
                'default': 'sql',
                'description': 'the storage backend, one of sql, redis, memory. memory is local only.',
            },

            'config_backend': {
                'default': 'sql',
                'description': """the config backend, choose one of:
                sql (postomaat compatible sql query)
                dbconfig (use fuglu dbconfig)
                file (static config file)
                """,
            },

            'dbconnection': {
                'default': "mysql://root@localhost/callahead?charset=utf8",
                'description': 'SQLAlchemy connection string for sql backend and sql config',
            },

            'redis_conn': {
                'default': 'redis://127.0.0.1:6379/1',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },

            'redis_timeout': {
                'default': '2',
                'description': 'redis backend timeout in seconds',
            },

            'cleanupinterval': {
                'default': '300',
                'description': 'memory backend cleanup interval',
            },

            'always_assume_rec_verification_support': {
                'default': "False",
                'description': """set this to true to disable the skiplisting of servers that don't support recipient verification"""
            },

            'always_accept': {
                'default': "False",
                'description': """Set this to always return 'continue' but still perform the recipient check and fill the cache (learning mode without rejects)"""
            },

            'keep_positive_history_time': {
                'default': '30',
                'description': """how long should expired positive cache data be kept in the table history [days] (sql only)"""
            },

            'keep_negative_history_time': {
                'default': '1',
                'description': """how long should expired negative cache data be kept in the table history [days] (sql only)"""
            },

            'messagetemplate': {
                'default': 'previously cached response: ${message}',
                'description': 'reject message template for previously cached responses'
            },

            'messagetemplate_directory_only': {
                'default': 'User unknown',
                'description': 'reject message template in positive directory mode'
            },

            'always_accept_regex': {
                'default': '',
                'description': 'always accept recipients if they match this regex. leave empty to omit'
            },

            'problemaction': {
                'default': 'tempfail',
                'description': "action if there is a problem (continue, tempfail)",
            },

            'verbose': {
                'default': 'False',
                'description': "enable extra verbose smtp test logging",
            },
            
            'proxy_url': {
                'default': '',
                'description': 'perform call-ahead lookups via socks proxy (e.g. socks5://user:pass@proxy:10025). requires pysocks'
            },

            'enabled': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'enable recipient verification',
            },

            'server': {
                'section': 'ca_default',
                'default': 'mx:${domain}',
                'description': 'how should we retrieve the next hop? define sql, static, txt, mx, tag',
            },

            'timeout': {
                'section': 'ca_default',
                'default': '30',
                'description': 'socket timeout',
            },

            'test_server_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if it doesn't support recipient verification [seconds]",
            },

            'positive_cache_time': {
                'section': 'ca_default',
                'default': str(7*86400),
                'description': 'how long should we cache existing addresses [seconds]',
            },

            'negative_cache_time': {
                'section': 'ca_default',
                'default': '14400',
                'description': 'how long should we keep negative cache entries [seconds]',
            },

            'test_fallback': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'if first server fails, try fallback relays?',
            },

            'smtp_port': {
                'section': 'ca_default',
                'default': '25',
                'description': 'check on this TCP port. defaults to 25 (smtp)',
            },

            'positive_directory_only': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'if set to True, do not perform call-ahead and consider missing entries in database to be negative/rejectable. This is useful if the entries for this domain are added via alternative means to the database (e.g. hardcoded or imported from a database/active directory/user listing)',
            },

            'testuser': {
                'section': 'ca_default',
                'default': 'rbxzg133-7tst',
                'description': 'test user that probably does not exist',
            },

            'sender': {
                'section': 'ca_default',
                'default': '${bounce}',
                'description': '${bounce}',
            },

            'use_tls': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'use opportunistic TLS if supported by server. set to False to disable tls',
            },

            'ssl_cert_tag': {
                'section': 'ca_default',
                'default': '',
                'description': 'get SSL cert data from tag. tag content must be a tuple of cert path, key path, key password',
            },

            'ssl_cert_file': {
                'section': 'ca_default',
                'default': '',
                'description': 'path to SSL client cert file. leave empty to not use client cert',
            },

            'ssl_key_file': {
                'section': 'ca_default',
                'default': '',
                'description': 'path to SSL client key file. leave empty to not use client cert',
            },

            'ssl_key_pass': {
                'section': 'ca_default',
                'default': '',
                'description': 'password to decrypt SSL client key file. leave empty if no password is neede',
            },

            'accept_on_tempfail': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'accept mail on temporary error (4xx) of target server, DEFER otherwise',
            },

            'defer_on_hostnotfound': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'defer instead of accept if target server has no A records defined.',
            },

            'defer_on_relayaccessdenied': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'defer instead of reject if target server says "Relay access denied"',
            },
            
            'tenantattributionerror_action': {
                'section': 'ca_default',
                'default': 'tempfail', # you may even want to use CONTINUE here
                'description': 'action if target server says "TenantInboundAttribution; There is a partner connector configured that matched..."',
            },

            'no_valid_server_fail_action': {
                'section': 'ca_default',
                'default': 'tempfail',  # you may even want to use REJECT here
                'description': "action if we don't find a server to ask",
            },

            'no_valid_server_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a recipient domain if we don't find a server to ask [seconds]",
            },

            'no_valid_server_fail_message': {
                'section': 'ca_default',
                'default': '${errormessage}',
                'description': "message template template if we don't find a server to ask",
            },

            'resolve_fail_action': {
                'section': 'ca_default',
                'default': 'tempfail',
                'description': "action if we can't resolve target server hostname",
            },

            'resolve_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we can't resolve target server hostname [seconds]",
            },

            'resolve_fail_message': {
                'section': 'ca_default',
                'default': '${errormessage}',
                'description': "message template if we can't resolve target server hostname",
            },

            'preconnect_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if we encounter a failure before connecting to target server (continue, tempfail, reject)",
            },

            'preconnect_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we encounter a failure before connecting to target server [seconds]",
            },

            'preconnect_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if we encounter a failure before connecting to target server",
            },

            'connect_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if we cannot connect to the target server (continue, tempfail, reject)",
            },

            'connect_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we cannot connect to the target server [seconds]",
            },

            'connect_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if we cannot connect to the target server",
            },

            'helo_name': {
                'section': 'ca_default',
                'default': '',
                'description': "HELO name for smtp test (empty: uses socket.getfqdn(), string: use string directly, string starting with '$' will get environment variable",
            },

            'helo_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server does not accept our HELO (continue, tempfail, reject)",
            },

            'helo_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server does not accept our HELO [seconds]",
            },

            'helo_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server does not accept our HELO (continue, tempfail, reject)",
            },

            'mail_from_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server does not accept our from address",
            },

            'mail_from_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server does not accept our from address [seconds]",
            },

            'mail_from_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server does not accept our from address",
            },

            'rcpt_to_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server show unexpected behaviour on presenting the recipient address (continue, tempfail, reject)",
            },

            'rcpt_to_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server show unexpected behaviour on presenting the recipient address [seconds]",
            },

            'rcpt_to_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server show unexpected behaviour on presenting the recipient address",
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    async def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        cache_storage = self.config.get(self.section, 'cache_storage')
        backend = self.config.get(self.section, 'config_backend')
        
        if not SQL_EXTENSION_ENABLED and (cache_storage=='sql' or backend=='sql'):
            print("ERROR: sqlalchemy is not installed")
            return False
        
        if not REDIS_ENABLED and (cache_storage=='redis' or backend=='redis'):
            print("ERROR: redis library is not installed")
            return False
        
        if cache_storage=='redis' or backend=='redis':
            password = self.config.get(self.section, 'redis_password', fallback=None) or None
            if password is not None:
                print('deprecatioin warning: obsolete redis_password configured, set via redis_conn')

        if not HAVE_DOMAINMAGIC:
            print('WARNING: domainmagic is not installed - some functionality will not be available')

        if not self.check_config():
            return False

        if self.config.get('ca_default', 'server').startswith('mx:') and not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
            print("ERROR: no DNS resolver library available - required for mx resolution")
            return False
        elif not aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED:
            print("WARNING: no DNS resolver library available - some functionality will not be available")

        if self.config.get(self.section, 'cache_storage') == 'redis' and not REDIS_ENABLED:
            print('ERROR: redis backend configured but redis python module not available')
            return False

        self._init_cache()
        if self.cache is None:
            print(f'ERROR: failed to initialize cache with storage {cache_storage}')
            return False
        else:
            ok = await self.cache.lint()
            if not ok:
                return False

        self._init_config_backend('lintuser@fuglu.org')
        try:
            poscount, negcount = await self.cache.get_total_counts()
            print(f"INFO: Addresscache: {poscount} positive entries, {negcount} negative entries")
        except Exception as e:
            print(f"ERROR: DB Connection failed: {e.__class__.__name__}: {str(e)}")
            return False

        test = SMTPTest(self.config, self.section)
        try:
            test.get_domain_config_float('lint', 'timeout')
        except Exception:
            print('WARNING: Could not get timeout value from config, using internal default of 10s')

        try:
            dbconnection = self.config.get(self.section, 'dbconnection')
            if dbconnection:
                conn = get_session(dbconnection)
                conn.execute(text("SELECT 1"))
        except Exception as e:
            print(f"ERROR: Failed to connect to SQL database: {e.__class__.__name__}: {str(e)}")
            return False
        
        proxy_url = self.config.get(self.section, 'proxy_url')
        if proxy_url and not HAVE_PYSOCKS:
            print('WARNING: proxy_url defined but dependency pysocks missing - not using proxy')
        elif proxy_url:
            try:
                urlparse(proxy_url)
            except Exception as e:
                print(f'ERROR: failed to parse proxy_url {proxy_url} due to {e.__class__.__name__}: {str(e)}')

        return True

    def __str__(self):
        return "Address Check"

    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        sess.tags['ca.cacheduser'] = None
        timetracker = TrackTimings(enable=self.enabletimetracker)
        self.logger.debug(f"{sess.id} timetracker enabled: {self.enabletimetracker}")
        from_address = force_uString(sess.sender)
        if from_address is None:
            self.logger.debug(f'{sess.id} No FROM address found')
            from_address = '<>'

        # check current recipient
        to_address = force_uString(recipient)
        if to_address is None:
            self.logger.error(f'{sess.id} No TO address found')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        if to_address and to_address.lower() == "postmaster":
            self.logger.info(f'{sess.id} Postmaster TO address found -> skip')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        always_accept_regex = self.config.get(self.section, 'always_accept_regex').strip()
        if always_accept_regex and re.match(always_accept_regex, to_address, re.I):
            self.logger.info(f'{sess.id} TO address {to_address} matches always accept regex {always_accept_regex}')
            return sm.CONTINUE

        if HAVE_DOMAINMAGIC:
            to_address = strip_batv(to_address)

        domain = sm.MilterSession.extract_domain(to_address)
        if domain is None:
            self.logger.error(f'{sess.id} No TO domain in recipient {to_address} found')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        # check cache
        self._init_cache()
        self._init_config_backend(to_address, self.config, self.section, sess)
        timetracker.tracktime("init-cache")

        # it's possible to get an error trying to get the cached value therefore
        # 2 attempts are made
        entry = None
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                entry = await self.cache.get_address(to_address)
                self.logger.debug(f'{sess.id} Get cached address {to_address} entry: {entry}')
            except Exception as e:
                if attempts:
                    self.logger.warning(f'{sess.id} Could not get cached address {to_address}: {str(e)}')
                else:
                    self.logger.error(f'{sess.id} Could not get cached address {to_address}: {str(e)}')
                    timetracker.report_plugintime(sess.id, str(self))
                    return sm.CONTINUE

        timetracker.tracktime("get_address from cache database")

        if entry is not None:
            positive, message = entry

            if positive:
                self.logger.info(f'{sess.id} accepting cached address {to_address}')
                timetracker.report_plugintime(sess.id, str(self))
                return sm.CONTINUE
            else:
                if self.config.getboolean(self.section, 'always_accept'):
                    self.logger.info(f'{sess.id} Learning mode - accepting despite negative cache entry')
                else:
                    self.logger.info(f'{sess.id} rejecting negative cached address {to_address} : {message}')
                    timetracker.report_plugintime(sess.id, str(self))

                    template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
                    templ_dict = sess.get_templ_dict()
                    templ_dict['message'] = message
                    rejectmessage = template.safe_substitute(templ_dict)
                    return sm.REJECT, rejectmessage
        else:
            self.logger.debug(f"{sess.id} Address {to_address} not in database or entry has expired")

        # load domain config
        try:
            domainconfig = self.config_backend.get_domain_config_all()
        except RESTAPIError as e:
            action = self._problemcode()
            self.logger.warning(f'{sess.id} {asm.RETCODE2STR.get(action)} due to RESTAPIError: {str(e)}')
            return action, 'Internal Server Error'
        timetracker.tracktime("domainconfig")

        if domainconfig is None:
            self.logger.debug(f'{sess.id} domain config for domain {domain} was empty')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        # enabled?
        test = SMTPTest(self.config, self.section, self.relaycache, sess)
        servercachetime = test.get_domain_config_int(domain, 'test_server_interval', domainconfig, fallback=3600)
        enabled = test.get_domain_config_bool(domain, 'enabled', domainconfig, fallback=True)
        timetracker.tracktime("cachetime-enabled")
        if not enabled:
            self.logger.info(f'{sess.id} {to_address}: call-aheads for domain {domain} are disabled')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        positive_directory_only = test.get_domain_config_bool(domain, 'positive_directory_only', domainconfig, fallback=False)
        testaddress = test.maketestaddress(domain, domainconfig)
        try:
            testentry = await self.cache.get_address(testaddress)
        except Exception as e:
            self.logger.warning(f'{sess.id} failed to get testaddress {testaddress} due to {e.__class__.__name__}: {str(e)}')
            testentry = None
        if positive_directory_only and testentry:
            # we require the test user to be present in directory as a safety mesaure
            # if it is not there, db got flushed/corrupted/outdated and user should be accepted
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate_directory_only'))
            templ_dict = sess.get_templ_dict()
            rejectmessage = template.safe_substitute(templ_dict)
            return sm.REJECT, rejectmessage

        # check skiplist
        relays = await test.get_relays(domain, domainconfig)
        timetracker.tracktime("get_relays")
        result = SMTPTestResult()
        timetracker.tracktime("SMTPTest")
        need_server_test = False
        relay = None
        if relays is None or len(relays) == 0:
            self.logger.error(f"{sess.id} no relay for domain {domain} found!")
            result.state = SMTPTestResult.TEST_FAILED
            result.errormessage = f"no relay for domain {domain} found"

        if relays is not None:
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig, fallback=30)
            except (ValueError, TypeError):
                timeout = 10
            sender = test.get_domain_config(domain, 'sender', domainconfig, {'bounce': '', 'originalfrom': from_address})
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig, fallback=True)
            try:
                smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
            except (ValueError, TypeError, KeyError, configparser.NoSectionError) as e:
                self.logger.debug(f'{sess.id} failed to retrieve smtp_port override due to {e.__class__.__name__}: {str(e)}')
                smtp_port = smtplib.SMTP_PORT

            # only check test address if really needed...
            # the world market leader's good m365 does not like being hammered with invalid rcpts
            addresses = [to_address]
            if testentry is not None:
                need_server_test = testentry[0]
            else:
                need_server_test = True
            if need_server_test:
                self.logger.info(f'{sess.id} need to test {testaddress}')
                addresses.append(testaddress)
            else:
                self.logger.info(f'{sess.id} skipping test of {testaddress}')

            test_relays = relays[:]
            if not test.get_domain_config_bool(domain, 'test_fallback', domainconfig, fallback=False):
                test_relays = relays[:1]  # skip all except first relay in list

            starttime = time.time()
            for relay in test_relays:
                self.logger.debug(f"{sess.id} testing relay {relay} for domain {domain}")
                try:
                    if await self.cache.is_skiplisted(domain, relay):
                        self.logger.info(f'{sess.id} {to_address}: server {relay} for domain {domain} is skiplisted for call-aheads, skipping')
                        timetracker.report_plugintime(sess.id, str(self))
                        return sm.CONTINUE
                except Exception as e:
                    action = self._problemcode()
                    self.logger.error(f'{sess.id} {asm.RETCODE2STR.get(action)} failed to query skiplist for {to_address} due to {e.__class__.__name__}: {str(e)}')
                    return action, 'Internal Server Error'

                # make sure we don't call-ahead ourselves
                if to_address == testaddress:
                    self.logger.error(f"{sess.id} call-ahead loop detected!")
                    try:
                        await self.cache.skiplist(domain, relay, servercachetime, SMTPTestResult.STAGE_CONNECT, 'call-ahead loop detected', sess.id)
                    except Exception as e:
                        self.logger.warning(f'{sess.id} failed to add skiplist entry for {domain} due to {e.__class__.__name__}: {str(e)}')
                    timetracker.report_plugintime(sess.id, str(self))
                    return sm.CONTINUE

                # perform call-ahead
                self.logger.debug(f"{sess.id} Testing relay {relay} for {addresses} from {sender or '<>'} with timeout {timeout} and tls {use_tls} at port {smtp_port}")
                result = await test.smtptest(relay, addresses, mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)
                self.logger.debug(f"{sess.id} Tested relay {relay} for {addresses} with result stage={result.stage} state={result.state} replies={result.rcptoreplies}")
                
                if result.stage == SMTPTestResult.STAGE_RCPT_TO:
                    # this server was tested until rcpt to - it's a functioning smtp relay
                    # we could additionally check if there was a 450 - we ignore that for now
                    break

                if time.time() > starttime + timeout:
                    self.logger.debug(f'{sess.id} skipping further relays - timeout exceeded')
                    break
            timetracker.tracktime("RelayTests")

        if result.state != SMTPTestResult.TEST_OK:
            action = sm.CONTINUE
            message = None

            for stage in [SMTPTestResult.STAGE_PRECONNECT, SMTPTestResult.STAGE_RESOLVE, SMTPTestResult.STAGE_CONNECT,
                          SMTPTestResult.STAGE_HELO, SMTPTestResult.STAGE_MAIL_FROM, SMTPTestResult.STAGE_RCPT_TO]:
                if result.stage == stage:
                    stageaction, messagetmpl, interval = self._get_stage_config(stage, test, domain, domainconfig,
                                                                                sessid=sess.id)
                    if messagetmpl is None:
                        messagetmpl = ''
                        self.logger.debug(f'{sess.id} message template for stage {stage} not defined')

                    template = _SuspectTemplate(messagetmpl)
                    templ_dict = sess.get_templ_dict()
                    templ_dict['relay'] = relay
                    templ_dict['stage'] = stage
                    templ_dict['errormessage'] = result.errormessage
                    message = template.safe_substitute(templ_dict)

                    if stageaction is not None:
                        action = stageaction
                    if interval is not None:
                        servercachetime = min(servercachetime, interval)
            
            # skiplist if we tested a relay AND testaddress was either not necessary to test or confirmed to be accepted
            if relay is not None and (testaddress not in result.rcptoreplies or result.rcptoreplies[testaddress][0] == SMTPTestResult.ADDRESS_OK):
                try:
                    await self.cache.skiplist(domain, relay, servercachetime, result.stage, result.errormessage, sess.id)
                    self.logger.warning(
                        f'{sess.id} problem testing recipient verification support on server {relay} in stage {result.stage}: {result.errormessage}. putting on skiplist.')
                except Exception as e:
                    self.logger.warning(f'{sess.id} failed to add skiplist entry for {domain} due to {e.__class__.__name__}: {str(e)}')
            timetracker.tracktime("SMTPTestResult.Test_OK-fail")
            timetracker.report_plugintime(sess.id, str(self))
            return action, message

        blreason = 'unknown'
        if need_server_test:
            addrstate, code, msg = result.rcptoreplies[testaddress]
            recverificationsupport = None
            if addrstate == SMTPTestResult.ADDRESS_OK:
                blreason = 'accepts any recipient'
                recverificationsupport = False
            elif addrstate == SMTPTestResult.ADDRESS_TEMPFAIL:
                blreason = f'temporary failure: {code} {msg}'
                self.logger.info(f'{sess.id} could not determine rcpt filter state: {testaddress} {code} {msg}')
            elif addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                recverificationsupport = True
            if recverificationsupport is not None:
                try:
                    await self.cache.put_address(testaddress, servercachetime, not recverificationsupport, msg, sess.id)
                except Exception as e:
                    self.logger.warning(f'{sess.id} failed to add recipient {testaddress} to cache due to {e.__class__.__name__}: {str(e)}')
            timetracker.tracktime("need_server_test")
        else:
            recverificationsupport = True

        # override: ignore recipient verification fail
        if self.config.getboolean(self.section, 'always_assume_rec_verification_support'):
            recverificationsupport = True

        if recverificationsupport:
            addrstate, code, msg = result.rcptoreplies[to_address]
            positive = True
            sess.tags['ca.cacheduser'] = True
            cachetime = test.get_domain_config_int(domain, 'positive_cache_time', domainconfig)

            # handle case where testadress got 5xx , but actual address got 4xx
            if addrstate == SMTPTestResult.ADDRESS_TEMPFAIL:
                self.logger.info(f'{sess.id} server {relay} for domain {domain}: '
                                 f'skiplisting for {servercachetime} seconds (tempfail: {msg})')
                try:
                    await self.cache.skiplist(domain, relay, servercachetime, result.stage, f'tempfail: {msg}', sess.id)
                except Exception as e:
                    self.logger.warning(f'{sess.id} failed to add skiplist entry for {domain} due to {e.__class__.__name__}: {str(e)}')
                timetracker.tracktime("recverificationsupport-tempfail")
                if test.get_domain_config_bool(domain, 'accept_on_tempfail', domainconfig):
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.CONTINUE
                else:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.TEMPFAIL, msg

            defer_on_hostnotfound = test.get_domain_config_bool(domain, 'defer_on_hostnotfound', domainconfig)
            if defer_on_hostnotfound and msg.endswith(('has no A records', 'host name could not be resolved')):
                return sm.TEMPFAIL, msg
            
            tenantattributionerror_action = sm.STR2RETCODE.get(test.get_domain_config(domain, 'tenantattributionerror_action', domainconfig), sm.CONTINUE)
            if 'TenantInboundAttribution' in msg:
                return tenantattributionerror_action, msg

            defer_on_relayaccessdenied = test.get_domain_config_bool(domain, 'defer_on_relayaccessdenied', domainconfig)
            if addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                positive = False
                sess.tags['ca.cacheduser'] = False
                cachetime = test.get_domain_config_int(domain, 'negative_cache_time', domainconfig)

            relayaccessdenied = 'relay access denied' in msg.lower()

            if not (relayaccessdenied and defer_on_relayaccessdenied):
                # don't cache if we defer
                try:
                    await self.cache.put_address(to_address, cachetime, positive, msg, sess.id)
                except Exception as e:
                    self.logger.warning(f'{sess.id} failed to add recipient {testaddress} in cache due to {e.__class__.__name__}: {str(e)}')
                neg = ""
                if not positive:
                    neg = "negative "
                self.logger.info(f"{sess.id} {neg}cached {to_address} for {cachetime} seconds ({msg})")

            timetracker.tracktime("recverificationsupport")
            if positive:
                timetracker.report_plugintime(sess.id, str(self), end=False)
                return sm.CONTINUE
            else:
                if self.config.getboolean(self.section, 'always_accept'):
                    self.logger.info(f'{sess.id} learning mode - accepting despite inexistent address')
                elif relayaccessdenied and defer_on_relayaccessdenied:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.TEMPFAIL, msg
                else:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.REJECT, msg

        else:
            self.logger.info(f'{sess.id} server {relay} for domain {domain}: '
                             f'skiplisting for {servercachetime} seconds ({blreason}) in stage {result.stage}')
            try:
                await self.cache.skiplist(domain, relay, servercachetime, result.stage, blreason, sess.id)
            except Exception as e:
                self.logger.warning(f'{sess.id} failed to add skiplist entry for {domain} due to {e.__class__.__name__}: {str(e)}')
            timetracker.tracktime("no-recverificationsupport")
        timetracker.report_plugintime(sess.id, str(self))
        return sm.CONTINUE

    def _get_stage_config(self, stage, test, domain, domainconfig, sessid: str = "<>"):
        try:
            interval = test.get_domain_config_int(domain, f'{stage}_fail_interval', domainconfig)
        except (ValueError, TypeError):
            interval = None
            self.logger.debug(f'{sessid} Invalid {stage}_fail_interval for domain {domain}')
        stageaction = sm.STR2RETCODE.get(test.get_domain_config(domain, f'{stage}_fail_action', domainconfig), sm.CONTINUE)
        message = test.get_domain_config(domain, f'{stage}_fail_message', domainconfig) or None

        return stageaction, message, interval


class BounceCheck(BackendMixin, ScannerPlugin):
    """
    Extract original recipient address from outgoing "undeliverable" bounce messages
    and put it in call ahead cache
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'cache_storage': {
                'default': 'sql',
                'description': 'the storage backend, one of sql, redis, memory. memory is local only.',
            },

            'dbconnection': {
                'default': "mysql://root@localhost/callahead?charset=utf8",
                'description': 'SQLAlchemy connection string for sql backend and sql config',
            },

            'redis_conn': {
                'default': 'redis://127.0.0.1:6379/1',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },

            'redis_timeout': {
                'default': '2',
                'description': 'redis backend timeout in seconds',
            },
            
            'subject_keywords': {
                'default': 'Undeliverable, Unzustellbar, Non remis, Non recapitabile, Onbestelbaar, Não entregue, Não é possível entregar, No se puede entregar, Non recapitabile, Kézbesíthetetlen, Не удается доставить, Не може да бъде доставено, 배달되지 않음, ',
                'description': 'comma separated list of keywords of which one must be present in subject'
            },
            
            'body_keywords': {
                'default': 'RecipientNotFound',
                'description': 'comma separated list of keywords of which one must be present in mail body'
            },
            
            'blockmessage': {
                'default': 'User unknown or bouncing',
                'description': 'error message to be presented to next sender of inbound mail'
            },
            
            'actioncode': {
                'default': 'REJECT',
                'description': "plugin action if qualified NDR was detected",
            },
            
            'rejectmessage': {
                'default': 'NDR not allowed - contact your mail administrator to enable recipient filtering',
                'description': 'reject message for qualified NDR'
            },
            
            'cache_time': {
                'default': '604800',
                'description': 'how long should we keep negative cache entries [seconds]',
            },
            
            'exceptionsfile': {
                'default': '',
                'description': 'path to file with exceptions that should not be listed. one per line. list full addresses or domains',
            }
        }
        self.exceptions = None
        
    def _get_ndr_domain(self, suspect:Suspect) -> tp.Optional[str]:
        """
        check if message is bounce and if so return bounce sender domain. returns None if not an eligible ndr/bounce.
        """
        if suspect.get_header('auto-submitted') != 'auto-replied':
            return None
        
        subject_keywords = self.config.getlist(self.section, 'subject_keywords')
        subject = suspect.get_header('subject')
        for kw in subject_keywords:
            if kw in subject:
                break
        else:
            return None
        
        body_keywords = self.config.getlist(self.section, 'body_keywords')
        if body_keywords:
            sf = SuspectFilter()
            textparts = sf.get_decoded_textparts(suspect, attachment=False)
            for textpart in textparts:
                for kw in body_keywords:
                    if kw in textpart:
                        break
                else: # break outer loop if inner loop sent break
                    continue
                break
            else:
                return None
        
        hdr_from_address = suspect.parse_from_type_header(header='From')
        if hdr_from_address and len(hdr_from_address[0]) == 2:
            hdr_from = hdr_from_address[0][1]
            lhs, from_domain = hdr_from.lower().rsplit('@',1)
            if lhs == 'postmaster':
               return from_domain
        return None
    
    
    async def _block_address(self, suspect:Suspect, bounce_emails:tp.Set[str]) -> bool:
        """
        add address to CA cache
        """
        blocked = False
        for addr in bounce_emails:
            addr = addr.lower()
            cachetime = self.config.getint(self.section, 'cache_time')
            msg = self.config.get(self.section, 'blockmessage')
            await self.cache.put_address(addr, cachetime, False, msg, suspect.id)
            self.logger.debug(f'{suspect.id} created negative cache entry for user {addr}')
            blocked = True
        return blocked
    
    
    def _get_bounce_emails(self, suspect:Suspect, bounce_domain:str) -> tp.Set[str]:
        """
        get eligible addresses from mail body
        - must be in same domain as from sender
        - from sender must not be in exception list
        - address must not be in exception list
        """
        exceptions = []
        if self.exceptions:
            exceptions = self.exceptions.get_list()
        if bounce_domain in exceptions:
            self.logger.debug(f'{suspect.id} skipping bounce: {bounce_domain} in exceptionlist')
            return set()
        
        emails = {e.lower() for e in suspect.get_tag('body.emails', {})}
        bounce_emails = {e for e in set(emails) if e.endswith(f'@{bounce_domain}') and not e in exceptions}
        return bounce_emails
    
    
    def _init_exceptionsfile(self):
        if self.exceptions is None:
            exceptionsfile = self.config.get(self.section, 'exceptionsfile')
            if exceptionsfile and os.path.exists(exceptionsfile):
                self.exceptions = FileList(exceptionsfile, lowercase=True)
        

    async def examine(self, suspect:Suspect):
        if suspect.from_address:
            return DUNNO
        
        emails = suspect.get_tag('body.emails')
        if not emails:
            return None
        
        bounce_domain = self._get_ndr_domain(suspect)
        if not bounce_domain:
            self.logger.debug(f'{suspect.id} skipping bounce: not an eligible bounce')
            return DUNNO
        
        self._init_exceptionsfile()
        bounce_emails = self._get_bounce_emails(suspect, bounce_domain)
        if len(bounce_emails)==1:
            self._init_cache(self.config, self.section)
            if not await self.cache.is_skiplisted_domain(bounce_domain):
                # not skiplisted means rcpt filtering after rcpt to is working
                self.logger.debug(f'{suspect.id} skipping bounce: domain {bounce_domain} is not skiplisted')
            else:
                blocked = await self._block_address(suspect, bounce_emails)
                if blocked:
                    actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
                    message = self.config.get(self.section, 'rejectmessage')
                    return actioncode, message
        elif len(bounce_emails)>1:
            self.logger.debug(f'{suspect.id} skipping bounce: too many addresses: {", ".join(emails)}')
        
        return DUNNO
    
    async def lint(self) -> bool:
        ok = self.check_config()
        if ok:
            self._init_cache()
            if self.cache is None:
                print(f'ERROR: failed to initialize cache')
                ok = False
            else:
                ok = await self.cache.lint()
        if ok:
            exceptionsfile = self.config.get(self.section, 'exceptionsfile')
            if exceptionsfile and not os.path.exists(exceptionsfile):
                print(f'WARNING: exceptionsfile {exceptionsfile} not found')
            
        return ok
    

class SMTPTestResult:
    STAGE_PRECONNECT = "preconnect"
    STAGE_RESOLVE = "resolve"
    STAGE_CONNECT = "connect"
    STAGE_HELO = "helo"
    STAGE_MAIL_FROM = "mail_from"
    STAGE_RCPT_TO = "rcpt_to"

    TEST_IN_PROGRESS = 0
    TEST_FAILED = 1
    TEST_OK = 2

    ADDRESS_OK = 0
    ADDRESS_DOES_NOT_EXIST = 1
    ADDRESS_TEMPFAIL = 2
    ADDRESS_UNKNOWNSTATE = 3

    def __init__(self):
        # at what stage did the test end
        self.stage = SMTPTestResult.STAGE_PRECONNECT
        # test ok or error
        self.state = SMTPTestResult.TEST_IN_PROGRESS
        self.errormessage = None
        self.relay = None

        # replies from smtp server
        #tuple: (code,text)
        self.banner = None
        self.heloreply = None
        self.mailfromreply = None

        # address verification
        #tuple: (ADDRESS_STATUS,code,text)
        self.rcptoreplies = {}

    def __str__(self):
        str_status = "in progress"
        if self.state == SMTPTestResult.TEST_FAILED:
            str_status = "failed"
        elif self.state == SMTPTestResult.TEST_OK:
            str_status = "ok"

        str_stage = "unknown"
        stagedesc = {
            SMTPTestResult.STAGE_PRECONNECT: "preconnect",
            SMTPTestResult.STAGE_RESOLVE: "resolve",
            SMTPTestResult.STAGE_CONNECT: 'connect',
            SMTPTestResult.STAGE_HELO: 'helo',
            SMTPTestResult.STAGE_MAIL_FROM: 'mail_from',
            SMTPTestResult.STAGE_RCPT_TO: 'rcpt_to'
        }
        if self.stage in stagedesc:
            str_stage = stagedesc[self.stage]

        desc = f"TestResult: relay={self.relay} status={str_status} stage={str_stage}"
        if self.state == SMTPTestResult.TEST_FAILED:
            desc = f"{desc} error={self.errormessage}"
            return desc

        addrstatedesc = {
            SMTPTestResult.ADDRESS_DOES_NOT_EXIST: 'no',
            SMTPTestResult.ADDRESS_OK: 'yes',
            SMTPTestResult.ADDRESS_TEMPFAIL: 'no (temp fail)',
            SMTPTestResult.ADDRESS_UNKNOWNSTATE: 'unknown'
        }

        for k,v  in self.rcptoreplies.items():
            statedesc = addrstatedesc[v[0]]
            desc = f'{desc}\n {k}: accepted={statedesc} code={v[1]} ({v[2]})'

        return desc


class TargetList(FileList):
    def _parse_lines(self, lines):
        newcontent = {}
        for line in lines:
            line = self._apply_linefilters(line)
            if line is not None:
                try:
                    domain, server = line.split()
                    try:
                        newcontent[domain].append(server)
                    except KeyError:
                        newcontent[domain] = [server]
                except ValueError:
                    self.logger.warning(f'invalid domain-target line: {line}')
        return newcontent


class TargetListSingleton:
    """
    Process singleton to store a default TargetList instance
    """

    instance = None
    procPID = None

    def __init__(self, *args, **kwargs):
        pid = os.getpid()
        logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
        if pid == TargetListSingleton.procPID and TargetListSingleton.instance is not None:
            logger.debug(f"Return existing {self.__class__.__name__} Singleton for process with pid: {pid}")
        else:
            if TargetListSingleton.instance is None:
                logger.info(f"Create {self.__class__.__name__} for process with pid: {pid}")
            elif TargetListSingleton.procPID != pid:
                logger.warning(f"Replace {self.__class__.__name__} (created by process {TargetListSingleton.procPID}) for process with pid: {pid}")

            TargetListSingleton.instance = TargetList(*args, **kwargs)
            TargetListSingleton.procPID = pid

    def __getattr__(self, name):
        return getattr(TargetListSingleton.instance, name)

def _smtplib_get_socket(self, host, port, timeout):
    # Patched SMTP._get_socket
    return socks.create_connection(
        (host, port),
        timeout,
        self.source_address,
        proxy_type=socks.SOCKS5,
        proxy_addr=self.proxy_url.hostname,
        proxy_port=int(self.proxy_url.port),
        proxy_username=self.proxy_url.username,
        proxy_password=self.proxy_url.password,
    )

class ProxySMTP(smtplib.SMTP):
    def __init__(self, host='', port=0, local_hostname=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None, proxy_url=None):
        super().__init__(host, port, local_hostname, timeout, source_address)
        if proxy_url:
            self.proxy_url = urlparse(proxy_url)
        else:
            self.proxy_url = None
    
    proxy_type = {
        'http': socks.HTTP,
        'socks4': socks.SOCKS4,
        'socks5': socks.SOCKS5,
    }
    
    def _get_socket(self, host, port, timeout):
        if self.proxy_url and HAVE_PYSOCKS:
            # Patched SMTP._get_socket
            return socks.create_connection(
                (host, port),
                timeout,
                self.source_address,
                proxy_type=self.proxy_type.get(self.proxy_url.scheme),
                proxy_addr=self.proxy_url.hostname,
                proxy_port=int(self.proxy_url.port),
                proxy_username=self.proxy_url.username,
                proxy_password=self.proxy_url.password,
            )
        else:
            return super()._get_socket(host, port, timeout)


class SMTPTest:
    def __init__(self, config=None, section=None, relaycache=None, miltersession=None):
        self.config = config
        self.section = section
        self.relaycache = relaycache
        self.logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
        if section is None:
            self.be_verbose = False
        else:
            self.be_verbose = self.config.getboolean(self.section, 'verbose', fallback=False)
        self.miltersession = miltersession

    def is_ip(self, value):
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def is_testaddress(self, address):
        domain = address.rsplit('@', 1)[-1]
        testaddr = self.maketestaddress(domain)
        return address == testaddr

    def maketestaddress(self, domain, domainconfig=None):
        """
        Return a static test address that probably doesn't exist.
        It is NOT randomly generated, so we can check if the incoming
        connection does not produce a call-ahead loop
        """
        testuser = self.get_domain_config(domain, 'testuser', domainconfig, {'domain': domain})
        return f"{testuser}@{domain}"

    def get_domain_config(self, domain, key, domainconfig=None, templatedict=None, fallback=''):
        """Get configuration value for domain or default. Apply template string if templatedict is not None"""
        defval = self.config.get('ca_default', key, fallback=fallback)

        theval = defval
        if domainconfig is None:  # nothing from sql
            # check config file overrides
            configbackend = ConfigFileBackend(self.config, self.section)
            configbackend.domain = domain

            # ask the config backend if we have a special server config
            backendoverride = configbackend.get_domain_config_value(key)
            if backendoverride is not None:
                theval = backendoverride
        elif key in domainconfig:
            theval = domainconfig[key]

        if templatedict is not None:
            theval = Template(theval).safe_substitute(templatedict)

        return theval

    def get_domain_config_int(self, domain, key, domainconfig=None, templatedict=None, fallback=None):
        value = self.get_domain_config(domain, key, domainconfig, templatedict, fallback)
        try:
            return int(value)
        except (ValueError, TypeError):
            return fallback

    def get_domain_config_float(self, domain, key, domainconfig=None, templatedict=None, fallback=None):
        value = self.get_domain_config(domain, key, domainconfig, templatedict, fallback)
        try:
            return float(value)
        except (ValueError, TypeError):
            return fallback

    def get_domain_config_bool(self, domain, key, domainconfig=None, templatedict=None, fallback=None):
        value = self.get_domain_config(domain, key, domainconfig, templatedict)
        if isinstance(value, bool):
            pass
        elif value:
            value = force_uString(value).lower()
        else:
            value = fallback
        if value in [True, "1", "yes", "true", "on"]:
            return True
        if value in [False, None, '', "0", "no", "false", "off"]:
            return False
        raise ValueError(f'not a boolean value: {value}')

    async def get_relays(self, domain, domainconfig=None):
        """Determine the relay(s) for a domain"""
        relays = None
        if self.relaycache is not None:
            relays = self.relaycache.get_cache(domain)
            if relays is not None:
                return relays

        serverconfig = self.get_domain_config(domain, 'server', domainconfig, {'domain': domain})
        if serverconfig:
            srctype, val = serverconfig.split(':', 1)
        else:
            srctype = 'none'
            val = ''

        if srctype == 'sql':
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            ret = conn.execute(text(val))
            relays = []
            for row in ret:
                for item in row:
                    relays.append(item)
            conn.remove()
        elif srctype == 'mx':
            relays = await aiodnsquery.mxlookup(val)
        elif srctype == 'static':
            relays = [val, ]
        elif srctype == 'txt':
            targetlist_from_file = TargetList(lowercase=True, filename=val)
            try:
                targetslist = targetlist_from_file.get_list()
                try:
                    relays = targetslist.get(domain.lower(), [])
                except Exception as e:
                    self.logger.error(
                        f"{self.miltersession.id} Error getting element for SMTPTest: domain->{domain}, in list {targetslist} -> {e.__class__.__name__}: {str(e)} -> serverconfig:{serverconfig}")
                    relays = []
            except Exception as e:
                self.logger.error(f'{self.miltersession.id} Error reading targetlist from {val} for {domain}: {e.__class__.__name__}: {str(e)}')
                relays = []
        elif srctype == 'tag':
            keylist = val.split(':')
            value = self.miltersession.tags
            for key in keylist:
                value = value.get(key, {})
                if isinstance(value, str):
                    relays = [value]
                elif isinstance(value, list):
                    relays = value
        elif srctype == 'none':
            self.logger.error(f'{self.miltersession.id} no relay lookup type found for {domain} in {serverconfig}')
        else:
            self.logger.error(f'{self.miltersession.id} unknown relay lookup type {srctype} for {domain} in {serverconfig}')

        if self.relaycache is not None and relays is not None:
            self.relaycache.put_cache(domain, relays)
        return relays

    async def smtptest(self, relay, addrlist, helo=None, mailfrom=None, timeout=10, use_tls=1, port=smtplib.SMTP_PORT):
        """perform a smtp check until the rcpt to stage
        returns a SMTPTestResult
        """

        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} Create SMTPTestResult object for {relay}:{port}")
        result = SMTPTestResult()
        result.relay = relay

        if mailfrom is None:
            mailfrom = ""

        if helo is None:
            heloinput = self.config.get('ca_default', 'helo_name', fallback='')
            if heloinput and heloinput.strip():
                heloinput = heloinput.strip()
                if heloinput.startswith('$') and heloinput[1:]:
                    # get from environment variable
                    helo = os.getenv(heloinput[1:], default=None)
                else:
                    helo = heloinput
            else:
                helo = get_outgoing_helo(self.config)
        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} HELO is: {helo}")

        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} STAGE_RESOLVE")
        result.stage = SMTPTestResult.STAGE_RESOLVE
        if aiodnsquery.AIODNSQUERY_EXTENSION_ENABLED and not self.is_ip(relay):
            arecs = await aiodnsquery.lookup(relay)
            if arecs is None:
                result.state = SMTPTestResult.TEST_FAILED
                result.errormessage = f"{self.miltersession.id} relay {relay} host name could not be resolved"
                return result
            elif arecs is not None and len(arecs) == 0:
                aaaarecs = await aiodnsquery.lookup(relay, 'AAAA')
                if not aaaarecs:
                    result.state = SMTPTestResult.TEST_FAILED
                    result.errormessage = f"{self.miltersession.id} relay {relay} has no A records"
                    return result

        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} STAGE_CONNECT")
        result.stage = SMTPTestResult.STAGE_CONNECT
        proxy_url = self.config.get(self.section, 'proxy_url', resolve_env=True)
        smtp = ProxySMTP(local_hostname=helo, proxy_url=proxy_url)
        smtp._host = relay  # work around tls initialisation bug in newer python 3.x versions
        smtp.timeout = timeout
        # smtp.set_debuglevel(True)
        if self.be_verbose:
            self.logger.debug(f'{self.miltersession.id} connecting to {relay}:{port} via {proxy_url}')
        try:
            code, msg = smtp.connect(relay, port=port)
            result.banner = (code, msg)
            if code < 200 or code > 299:
                result.state = SMTPTestResult.TEST_FAILED
                result.errormessage = f"relay {relay}:{port} did not accept connection: {force_uString(msg)}"
                return result
        except Exception as e:
            result.errormessage = f'{e.__class__.__name__}: {str(e)}'
            result.state = SMTPTestResult.TEST_FAILED
            self.logger.debug(f"{self.miltersession.id} error in stage=connect relay={relay}:{port} due to {e.__class__.__name__}: {str(e)}")
            return result

        # HELO
        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} STAGE_HELO")
        result.stage = SMTPTestResult.STAGE_HELO
        try:
            code, msg = smtp.ehlo()
            result.heloreply = (code, msg)
            if 199 < code < 300:
                if smtp.has_extn('STARTTLS') and use_tls:
                    # according to https://docs.python.org/3/library/ssl.html#ssl-security
                    context = ssl.create_default_context()

                    # ignore cert errors (like expired certificates, ...)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    certfile = keyfile = keypass = None
                    cert_tag = self.config.get('ca_default', 'ssl_cert_tag', fallback='')
                    if cert_tag:
                        data = self.miltersession.tags.get(cert_tag)
                        if data is not None:
                            certfile, keyfile, keypass = data
                    
                    if certfile is None or keyfile is None:
                        certfile = self.config.get('ca_default', 'ssl_cert_file', fallback='') or None
                        keyfile = self.config.get('ca_default', 'ssl_key_file', fallback='') or None
                        keypass = self.config.get('ca_default', 'ssl_key_pass', fallback='') or None
                    if certfile and os.path.exists(certfile) and keyfile and os.path.exists(keyfile):
                        try:
                            if self.be_verbose:
                                self.logger.debug(f'{self.miltersession.id} using cert {certfile} with key {keyfile}')
                            context.load_cert_chain(certfile, keyfile, keypass)
                        except (ssl.SSLError, PermissionError) as e:
                            self.logger.warning(f'{self.miltersession.id} could not load cert {certfile} with key {keyfile} due to {e.__class__.__name__}: {str(e)}')

                    if not smtp._host:
                        smtp._host = relay

                    code, msg = smtp.starttls(context=context)
                    if 199 < code < 300:
                        code, msg = smtp.ehlo()
                        if code < 200 or code > 299:
                            result.state = SMTPTestResult.TEST_FAILED
                            result.errormessage = f"relay {relay} did not accept EHLO after STARTTLS: {force_uString(msg)}"
                            return result
                    else:
                        self.logger.info(f'{self.miltersession.id} relay {relay} did not accept starttls: {code} {force_uString(msg)}')
                else:
                    self.logger.info(f'{self.miltersession.id} relay {relay} does not support starttls: {code} {force_uString(msg)}')
            else:
                self.logger.info(f'{self.miltersession.id} relay {relay} does not support esmtp, falling back')
                code, msg = smtp.helo()
                if code < 200 or code > 299:
                    result.state = SMTPTestResult.TEST_FAILED
                    result.errormessage = f"relay {relay} did not accept HELO: {force_uString(msg)}"
                    return result
        except Exception as e:
            result.errormessage = f'{e.__class__.__name__}: {str(e)}'
            result.state = SMTPTestResult.TEST_FAILED
            self.logger.debug(f"{self.miltersession.id} error in stage=helo relay={relay}:{port} due to {e.__class__.__name__}: {str(e)}")
            return result

        # MAIL FROM
        if self.be_verbose:
            self.logger.debug(f"{self.miltersession.id} STAGE_MAIL_FROM")
        result.stage = SMTPTestResult.STAGE_MAIL_FROM
        try:
            code, msg = smtp.mail(mailfrom)
            result.mailfromreply = (code, msg)
            if code < 200 or code > 299:
                result.state = SMTPTestResult.TEST_FAILED
                result.errormessage = f"relay {relay} did not accept MAIL FROM: {force_uString(msg)}"
                return result
        except Exception as e:
            result.errormessage = f'{e.__class__.__name__}: {str(e)}'
            result.state = SMTPTestResult.TEST_FAILED
            self.logger.debug(f"{self.miltersession.id} error in stage=mailfrom relay={relay}:{port} due to {e.__class__.__name__}: {str(e)}")
            return result

        # RCPT TO
        if self.be_verbose:
            self.logger.debug(f"STAGE_RCPT_TO")
        result.stage = SMTPTestResult.STAGE_RCPT_TO
        try:
            addrstate = SMTPTestResult.ADDRESS_UNKNOWNSTATE
            for addr in addrlist:
                if addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST and self.is_testaddress(addr):
                    # we can skip test address check if real rcpt addr does not exist
                    result.rcptoreplies[addr] = (addrstate, code, 'skipped test address check')
                    self.logger.debug(f'{self.miltersession.id} skipped test addres check for {addr} - rcpt filter already confirmed')
                    continue

                code, msg = smtp.rcpt(addr)
                if 199 < code < 300:
                    addrstate = SMTPTestResult.ADDRESS_OK
                elif 399 < code < 500:
                    addrstate = SMTPTestResult.ADDRESS_TEMPFAIL
                elif 499 < code < 600:
                    addrstate = SMTPTestResult.ADDRESS_DOES_NOT_EXIST
                else:
                    addrstate = SMTPTestResult.ADDRESS_UNKNOWNSTATE

                putmsg = f"relay {relay} said: {force_uString(msg)}"
                result.rcptoreplies[addr] = (addrstate, code, putmsg)
        except Exception as e:
            result.errormessage = f'{e.__class__.__name__}: {str(e)}'
            result.state = SMTPTestResult.TEST_FAILED
            self.logger.debug(f"{self.miltersession.id} error in stage=rcptto relay={relay}:{port} due to {e.__class__.__name__}: {str(e)}")
            return result

        result.state = SMTPTestResult.TEST_OK

        try:
            smtp.quit()
        except Exception as e:
            if self.be_verbose:
                self.logger.debug(f"{self.miltersession.id} error in stage=quit relay={relay}:{port} due to {e.__class__.__name__}: {str(e)}")
        return result


class CallAheadCacheInterface:
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')

    async def skiplist(self, domain, relay, expires, failstage=SMTPTestResult.STAGE_RCPT_TO, reason='unknown', fugluid=None):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        self.logger.error('skiplist:not implemented')

    async def is_skiplisted(self, domain, relay):
        """Returns True if the domain/relay combination is currently skiplisted and should not be used for recipient verification"""
        self.logger.error('is_skiplisted: not implemented')
        return False
    
    async def is_skiplisted_domain(self, domain):
        """Returns True if the domain is currently skiplisted and should not be used for recipient verification"""
        self.logger.error('is_skiplisted: not implemented')
        return False

    async def get_skiplist(self):
        """return all skiplisted servers"""
        self.logger.error('get_skiplist: not implemented')
        # expected format per item: domain, relay, reason, expiry timestamp
        return []

    async def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        self.logger.error('unskiplist: not implemented')
        return 0

    async def wipe_domain(self, domain, positive=None):
        self.logger.error('wipe_domain: not implemented')
        return 0

    async def get_all_addresses(self, domain):
        self.logger.error('get_all_addresses: not implemented')
        return []

    async def put_address(self, address, expires, positiveEntry=True, message=None, fugluid=None):
        """add address to cache"""
        self.logger.error('put_address: not implemented')

    async def get_address(self, address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        self.logger.error('get_address: not implemented')
        return None

    async def wipe_address(self, address):
        """remove address from cache"""
        self.logger.error('wipe_address: not implemented')
        return 0

    async def get_total_counts(self):
        self.logger.error('get_total_counts: not implemented')
        return 0, 0

    async def cleanup(self):
        self.logger.error('cleanup: not implemented')
        return 0, 0, 0

    async def lint(self):
        self.logger.warning('lint: not implemented')
        return True  # we still consider the test to be successful


if SQL_EXTENSION_ENABLED:
    class SQLSkiplist(DeclarativeBase):
        __tablename__ = 'fuglu_ca_skiplist'
        __table_args__ = (
            UniqueConstraint("domain", "relay"),
        )
        list_id = Column(Integer, primary_key=True)
        domain = Column(Unicode(255), nullable=False)
        relay = Column(Unicode(255), nullable=False)
        expiry_ts = Column(TIMESTAMP, nullable=False)
        check_stage = Column(Unicode(10), nullable=False)
        reason = Column(Unicode(255), nullable=True)
        fuglu_id = Column(Unicode(32), nullable=True)
    
    class SQLAddressCache(DeclarativeBase):
        __tablename__ = 'fuglu_ca_addresscache'
        entry_id = Column(Integer, primary_key=True)
        domain = Column(Unicode(255), nullable=False)
        email = Column(Unicode(255), nullable=False, unique=True)
        expiry_ts = Column(TIMESTAMP, nullable=False)
        positive = Column(Boolean, nullable=False)
        message = Column(Unicode(255), nullable=True)
        fuglu_id = Column(Unicode(32), nullable=True)

class MySQLCache(CallAheadCacheInterface):
    def __init__(self, config, section):
        super().__init__(config, section)
        self.conn = self.config.get(self.section, 'dbconnection')
        
    def _sql_conn_commit(self, conn):
        if sql_alchemy_version == SQL_ALCHEMY_V2:
            conn.commit()
        elif sql_alchemy_version == SQL_ALCHEMY_V1:
            conn.remove()
        else:
            self.logger.warning(f'wipe_address: unknown sql_alchemy_version {sql_alchemy_version}')

    async def skiplist(self, domain, relay, seconds, failstage='rcpt_to', reason='unknown', fugluid=None):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        entry = SQLSkiplist()
        entry.domain = domain
        entry.relay = relay
        entry.expiry_ts = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        entry.check_stage = failstage
        entry.reason = reason
        entry.fuglu_id = fugluid
        
        conn = get_session(self.conn)
        conn.add(entry)
        conn.flush()
        self._sql_conn_commit(conn)

    async def is_skiplisted(self, domain, relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        conn = get_session(self.conn)
        if not conn:
            return False
        result = conn.query(SQLSkiplist).filter(SQLSkiplist.domain==domain).filter(SQLSkiplist.relay==relay).filter(SQLSkiplist.expiry_ts>=datetime.datetime.now()).first()
        sc = result is not None
        return sc
    
    async def is_skiplisted_domain(self, domain):
        """Returns True if the domain is currently skiplisted and should not be used for recipient verification"""
        conn = get_session(self.conn)
        result = conn.query(SQLSkiplist).filter(SQLSkiplist.domain==domain).filter(SQLSkiplist.expiry_ts>=datetime.datetime.now()).first()
        sc = result is not None
        return sc

    async def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        conn = get_session(self.conn)
        result = conn.query(SQLSkiplist).filter(or_(SQLSkiplist.domain==relayordomain, SQLSkiplist.relay==relayordomain)).delete()
        conn.flush()
        self._sql_conn_commit(conn)
        return result

    async def get_skiplist(self):
        """return all skiplisted servers"""
        conn = get_session(self.conn)
        if not conn:
            return
        result = conn.query(SQLSkiplist).filter(SQLSkiplist.expiry_ts>=datetime.datetime.now()).order_by(SQLSkiplist.domain).all()
        ret = [row for row in result]
        return ret

    async def wipe_address(self, address):
        conn = get_session(self.conn)
        if not conn:
            return None
        result = conn.query(SQLAddressCache).filter(SQLAddressCache.email==address).delete()
        conn.flush()
        self._sql_conn_commit(conn)
        return result

    async def cleanup(self):
        conn = get_session(self.conn)
        postime = self.config.getint('AddressCheck', 'keep_positive_history_time')
        negtime = self.config.getint('AddressCheck', 'keep_negative_history_time')
        now=datetime.datetime.now()
        poscount = conn.query(SQLAddressCache).filter(SQLAddressCache.positive==True).filter(SQLAddressCache.expiry_ts<now-datetime.timedelta(seconds=postime)).delete()
        negcount = conn.query(SQLAddressCache).filter(SQLAddressCache.positive==False).filter(SQLAddressCache.expiry_ts<now-datetime.timedelta(seconds=negtime)).delete()
        blcount =  conn.query(SQLSkiplist).filter(SQLSkiplist.expiry_ts<now).delete()
        conn.flush()
        self._sql_conn_commit(conn)
        return poscount, negcount, blcount

    async def wipe_domain(self, domain, positive=None):
        """wipe all cache info for a domain. 
        if positive is None(default), all cache entries are deleted. 
        if positive is False all negative cache entries are deleted
        if positive is True, all positive cache entries are deleted
        """
        conn = get_session(self.conn)
        if not conn:
            return None
        
        query = conn.query(SQLAddressCache).filter(SQLAddressCache.domain==domain)
        if positive is not None:
            query = query.filter(SQLAddressCache.positive==positive)
        result = query.delete()
        conn.flush()
        self._sql_conn_commit(conn)
        return result

    async def put_address(self, address, seconds, positiveEntry=True, message=None, fugluid=None):
        """put address into the cache"""
        conn = get_session(self.conn)
        if not conn:
            return None
        
        domain = sm.MilterSession.extract_domain(address)
        entry = SQLAddressCache()
        entry.domain = domain
        entry.email = address
        entry.expiry_ts = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        entry.positive = positiveEntry
        entry.message = message
        entry.fuglu_id = fugluid
        conn.add(entry)
        conn.flush()
        self._sql_conn_commit(conn)

    async def get_address(self, address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        conn = get_session(self.conn)
        if not conn:
            return None
        res = conn.query(SQLAddressCache).filter(SQLAddressCache.email==address).filter(SQLAddressCache.expiry_ts>=datetime.datetime.now()).first()
        if res:
            result = [res.positive, res.message]
        else:
            result = None
        return result

    async def get_all_addresses(self, domain):
        conn = get_session(self.conn)
        if not conn:
            return None
        result = conn.query(SQLAddressCache).filter(SQLAddressCache.expiry_ts>=datetime.datetime.now()).order_by(SQLAddressCache.email).all()
        ret = [[x.email, x.positive] for x in result]
        return ret

    async def get_total_counts(self):
        conn = get_session(self.conn)
        poscount = conn.query(SQLAddressCache).filter(SQLAddressCache.positive==True).filter(SQLAddressCache.expiry_ts>=datetime.datetime.now()).count()
        negcount = conn.query(SQLAddressCache).filter(SQLAddressCache.positive==False).filter(SQLAddressCache.expiry_ts>=datetime.datetime.now()).count()
        return poscount, negcount

    async def lint(self):
        try:
            conn = get_session(self.conn)
            conn.execute(text('SELECT 1'))
            return True
        except Exception as e:
            print(f'Failed to connect to database: {e.__class__.__name__} {str(e)}')
            return False


class RedisAddress:
    def __init__(self, address, positive, message, comment=None, fugluid=None):
        self.data = dict()
        self.data['address'] = address
        self.data['domain'] = address.rsplit('@', 1)[-1]
        self.data['positive'] = str(positive)
        self.data['message'] = message
        self.data['comment'] = comment or message
        self.data['check_ts'] = utcnow().isoformat(sep=' ', timespec='seconds')
        self.data['fugluid'] = fugluid or 'n/a'


class RedisCache(CallAheadCacheInterface):
    def __init__(self, config, section):
        super().__init__(config, section)
        self._aioredisbackend = None
        self.logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
        self.timeout = self.config.get(self.section, 'redis_timeout', fallback=3)
    
    @property
    def aioredisbackend(self) -> AIORedisBaseBackend:
        if self._aioredisbackend is None:
            redis_url = self.config.get(self.section, 'redis_conn')
            self._aioredisbackend = AIORedisBaseBackend(redis_url=redis_url, logger=self.logger)
        return self._aioredisbackend
    
    async def _get_redis_pipeline(self):
        rds = await self.aioredisbackend.get_redis()
        return await rds.pipeline()
    
    async def _update(self, name, values, ttl):
        """atomic update of hash value and ttl in redis"""
        pipe = await self._get_redis_pipeline()
        nobools = {}
        for k, v in values.items():
            if v is None:
                pass
            elif isinstance(v, bool):
                nobools[k] = str(v)
            else:
                nobools[k] = v
        
        pipe.hset(force_bString(name), mapping=nobools)
        pipe.expire(force_bString(name), ttl)
        await pipe.execute()

    async def _multiget(self, names, keys):
        """atomically gets multiple hashes from redis"""
        pipe = await self._get_redis_pipeline()
        for name in names:
            pipe.hmget(force_bString(name), keys)
        items = await pipe.execute()
        self.logger.debug(f"Got {items} for names:{names} and keys:{keys}")
        return items
    
    async def _multidel(self, names) -> int:
        delcount = 0
        if names:
            pipe = await self._get_redis_pipeline()
            for name in names:
                pipe.delete(force_bString(name))
            result = await pipe.execute()
            for item in result:
                if item:
                    delcount += item
        return delcount

    async def _keys(self, match='*'):
        resulting_keys = []
        async for keybatch in self.aioredisbackend.scan_iter(match=match, count=250, timeout=self.timeout):
            async for key in keybatch:
                resulting_keys.append(key)
        self.logger.debug(f"Got {len(resulting_keys)} for match {match}")
        return resulting_keys

    def __pos2bool(self, entry, idx):
        """converts string boolean value in list back to boolean"""
        if entry is None or len(entry) < idx:
            pass
        value = force_uString(entry[idx])
        if value == 'True':
            entry[idx] = True
        elif value == 'False':
            entry[idx] = False

    async def skiplist(self, domain:str, relay:str, expires:int, failstage:str=SMTPTestResult.STAGE_RCPT_TO, reason:str='unknown', fugluid:str=None) -> None:
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        domain = domain.lower()
        name = f'relay-{relay}-{domain}'
        values = {
            'domain': domain,
            'relay': relay.lower(),
            'check_stage': failstage,
            'reason': reason,
            'check_ts': utcnow().isoformat(sep=' ', timespec='seconds'),
            'fugluid': fugluid or 'n/a',
        }
        rdis = await self.aioredisbackend.get_redis()
        expires = max(expires, await rdis.ttl(name))
        await self._update(name, values, expires)

    async def unskiplist(self, relayordomain:str) -> int:
        """remove a server from the skiplist/history"""
        names = await self._keys(f'relay-*{relayordomain.lower()}*')
        delcount = await self._multidel(names)
        return delcount

    async def is_skiplisted(self, domain:str, relay:str) -> bool:
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        name = f'relay-{relay.lower()}-{domain.lower()}'
        skiplisted = await self.aioredisbackend.exists(name, timeout=self.timeout)
        return skiplisted
    
    async def is_skiplisted_domain(self, domain:str) -> bool:
        """Returns True if the domain is currently skiplisted and should not be used for recipient verification"""
        name = f'relay-*-{domain.lower()}'
        names = await self._keys(name)
        listed = False
        if names:
            listed = True
        return listed

    async def get_skiplist(self) -> tp.List[tp.List[str]]:
        """return all skiplisted servers"""
        names = await self._keys('relay-*')
        items = []
        for name in names:
            result = await self.aioredisbackend.hmget(force_bString(name), ['domain', 'relay', 'reason'], timeout=self.timeout)
            ttl = await self.aioredisbackend.ttl(force_bString(name), timeout=self.timeout)
            ts = utcnow() + datetime.timedelta(seconds=ttl)
            item = []
            for idx in range(0, 3):
                item.append(force_uString(result[idx]))
            item.append(ts.isoformat(sep=' ', timespec='seconds'))
            items.append(item)
        items.sort(key=lambda x: x[0])
        return items

    async def wipe_domain(self, domain:str, positive:str=None) -> int:
        """remove all addresses in given domain from cache"""
        if positive is not None:
            positive = positive.lower()
        names = await self._keys(f'addr-*@{domain.lower()}')

        if positive is None or positive == 'all':
            delkeys = names
        else:
            entries = await self._multiget(names, ['address', 'positive'])
            delkeys = []
            for item in entries:
                addr = item[0].decode()
                if positive == 'positive' and item[1] == b'True':
                    delkeys.append(f'addr-{addr}')
                elif positive == 'negative' and item[1] == b'False':
                    delkeys.append(f'addr-{addr}')
        
        delcount = await self._multidel(delkeys)
        return delcount

    async def get_all_addresses(self, domain:str) -> tp.List[tp.Tuple[str, bool]]:
        """get all addresses in given domain from cache"""
        names = await self._keys(f'addr-*@{domain}')
        entries = await self._multiget(names, ['address', 'positive'])
        for item in entries:
            self.__pos2bool(item, 1)
            item[0] = force_uString(item[0])
        return entries

    async def put_address(self, address:str, expires:int, positiveEntry:bool=True, message:str=None, fugluid:str=None):
        """put address in cache"""
        address = address.lower()
        name = f'addr-{address.lower()}'
        values = RedisAddress(address, positiveEntry, message, fugluid)
        expires = max(expires, await self.aioredisbackend.ttl(force_bString(name), timeout=self.timeout))
        await self._update(name, values.data, expires)

    async def get_address(self, address:str) -> tp.Tuple[bool, str]|None:
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        name = f'addr-{address.lower()}'
        entry = await self.aioredisbackend.hmget(name.encode(), ['positive', 'message'], timeout=self.timeout)
        if entry[0] is not None:
            self.__pos2bool(entry, 0)
        else:
            entry = None

        if entry is not None and entry[1] is not None:
            entry[1] = force_uString(entry[1])
        return entry

    async def wipe_address(self, address:str) -> int:
        """remove given address from cache"""
        names = await self._keys(f'addr-{address.lower()}')
        delcount = await self._multidel(names)
        return delcount

    async def get_total_counts(self) -> tp.Tuple[int, int]:
        """return how many positive and negative entries are in cache"""
        names = await self._keys('addr-*')
        entries = await self._multiget(names, ['positive'])
        poscount = negcount = 0
        for item in entries:
            if item[0] == b'True':
                poscount += 1
            else:
                negcount += 1
        return poscount, negcount

    def cleanup(self):
        # nothing to do on redis
        return 0, 0, 0

    async def lint(self):
        reply = await self.aioredisbackend.ping(timeout=self.timeout)
        if not reply:
            print('Failed to connect to Redis DB')
        return reply


class MemoryCache(CallAheadCacheInterface):
    def __init__(self, config, section):
        super().__init__(config, section)
        self.cleanupinterval = self.config.getint(self.section, 'cleanupinterval', fallback=3600)
        self.cache = {}  # it would probably be faster to have two local caches, one for relays and one for addresses
        self.lock = threading.Lock()

        t = threading.Thread(target=self._clear_cache_thread)
        t.daemon = True
        t.start()

    def _clear_cache_thread(self):
        while True:
            time.sleep(self.cleanupinterval)
            now = time.time()
            gotlock = self.lock.acquire(True)
            if not gotlock:
                continue

            cleancount = 0

            for key in self.cache.keys()[:]:
                obj, exptime = self.cache[key]
                if now > exptime:
                    del self.cache[key]
                    cleancount += 1
            self.lock.release()
            self.logger.debug(f"Cleaned {cleancount} expired entries.")

    def _put(self, key, obj, exp):
        now = time.time()
        expiration = now + exp

        gotlock = self.lock.acquire(True)
        if gotlock:
            if key in self.cache:
                exptime = self.cache[key][1]
                expiration = max(expiration, exptime)
            self.cache[key] = (obj, expiration)
            self.lock.release()

    def _get(self, key) -> tp.Optional[tp.Dict]:
        obj, exptime = self.cache.get(key, (None, 0))
        if obj is not None:
            now = time.time()
            if now > exptime:
                obj = None
        return obj

    async def skiplist(self, domain, relay, expires, failstage=SMTPTestResult.STAGE_RCPT_TO, reason='unknown', fugluid=None):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        name = f'relay-{relay}-{domain}'
        values = {
            'domain': domain,
            'relay': relay,
            'check_stage': failstage,
            'reason': reason,
            'check_ts': utcnow().isoformat(sep=' ', timespec='seconds'),
            'fugluid': fugluid or 'n/a',
        }
        self._put(name, values, expires)

    async def is_skiplisted(self, domain, relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        name = f'relay-{relay}-{domain}'
        item = self._get(name)
        if item is not None:
            return True
        else:
            return False
    
    async def is_skiplisted_domain(self, domain):
        """Returns True if the domain is currently skiplisted and should not be used for recipient verification"""
        skiplist = await self.get_skiplist()
        for item in skiplist:
            if item[0] == domain:
                return True
        return False

    async def get_skiplist(self):
        """return all skiplisted servers"""
        # expected format per item: domain, relay, reason, expiry timestamp
        items = []
        gotlock = self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in self.cache.keys():
                if name.startswith('relay-'):
                    obj, exptime = self.cache.get(name)
                    if now < exptime:
                        expts = datetime.datetime.fromtimestamp(exptime)
                        item = [obj.get('domain'), obj.get('relay'), obj.get('reason'), expts.isoformat(sep=' ', timespec='seconds')]
                        items.append(item)
            items.sort(key=lambda x: x[0])
            self.lock.release()
        return items

    async def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        delcount = 0
        gotlock = self.lock.acquire(True)
        if gotlock:
            for name in list(self.cache.keys())[:]:
                if name.startswith('relay-') and relayordomain in name:
                    del self.cache[name]
                    delcount += 1
            self.lock.release()
        return delcount

    async def wipe_domain(self, domain, positive=None):
        delcount = 0

        if positive is not None:
            positive = positive.lower()
        if positive is None or positive == 'all':
            delall = True
        else:
            delall = False

        gotlock = self.lock.acquire(True)
        if gotlock:
            for name in list(self.cache.keys())[:]:
                if name.startswith('addr-') and name.endswith(f'-{domain}'):
                    if delall:
                        del self.cache[name]
                        delcount += 1
                    else:
                        obj, exptime = self.cache[name]
                        if obj.get('positive') and positive == 'positive':
                            del self.cache[name]
                            delcount += 1
                        elif not obj.get('positive') and positive == 'negative':
                            del self.cache[name]
                            delcount += 1
            self.lock.release()

        return delcount

    async def get_all_addresses(self, domain):
        entries = []
        gotlock = self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in list(self.cache.keys())[:]:
                if name.startswith('addr-') and name.endswith(f'@{domain}'):
                    obj, exptime = self.cache.get(name, ({}, 0))
                    if now < exptime and obj:
                        entries.append((obj.get('address'), obj.get('positive')))
            self.lock.release()
        return entries

    async def put_address(self, address, expires, positiveEntry=True, message=None, fugluid=None):
        """add address to cache"""
        name = f'addr-{address.lower()}'
        domain = sm.MilterSession.extract_domain(address)
        values = {
            'address': address,
            'domain': domain,
            'positive': positiveEntry,
            'message': message,
            'check_ts': utcnow().isoformat(sep=' ', timespec='seconds'),
            'fugluid': fugluid or 'n/a',
        }
        self._put(name, values, expires)

    async def get_address(self, address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        obj = self._get(f'addr-{address.lower()}')
        if obj:
            entry = (obj.get('positive'), obj.get('message'))
        else:
            entry = None
        return entry

    async def wipe_address(self, address):
        """remove address from cache"""
        delcount = 0
        gotlock = self.lock.acquire(True)
        if gotlock:
            name = f'addr-{address.lower()}'
            if name in self.cache:
                del self.cache[name]
                delcount = 1
            self.lock.release()
        return delcount

    async def get_total_counts(self):
        poscount = negcount = 0
        gotlock = self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in self.cache.keys():
                obj, exptime = self.cache.get(name)
                if now < exptime:
                    if obj.get('positive'):
                        poscount += 1
                    else:
                        negcount += 1
            self.lock.release()
        return poscount, negcount

    async def cleanup(self):
        # nothing to do in memcache
        return 0, 0, 0

    async def lint(self):
        return True


class ConfigBackendInterface:
    def __init__(self, config, section):
        self.logger = logging.getLogger(f'fuglu.plugin.ca.{self.__class__.__name__}')
        self.config = config
        self.section = section
        self.domain = None
        self.recipient = None
        self.sess = MockSession()
        self.sess.id = 'unknown'
        self.tagconfig = None

    def set_rcpt(self, recipient):
        domain = recipient.rsplit('@', 1)[-1]
        self.domain = domain
        self.recipient = recipient
    
    def set_sess(self, sess, tagconfig=None):
        self.sess = sess
        self.tagconfig = tagconfig

    def get_domain_config_value(self, key):
        """return a single config value for this domain"""
        self.logger.error(f"{self.sess.id} get_domain_config_value: not implemented")
        return None

    def get_domain_config_all(self):
        """return all config values for this domain"""
        self.logger.error(f"{self.sess.id} get_domain_config_value: not implemented")
        return {}


if SQL_EXTENSION_ENABLED:
    class SQLConfigValue(DeclarativeBase):
        __tablename__ = 'fuglu_ca_configoverride'
        __table_args__ = (
            UniqueConstraint("domain", "confkey"),
        )
        entry_id = Column(Integer, primary_key=True)
        domain = Column(Unicode(255), nullable=False)
        confkey = Column(Unicode(255), nullable=False)
        confvalue = Column(Unicode(255), nullable=False)
    

class MySQLConfigBackend(ConfigBackendInterface):
    def get_domain_config_value(self, key):
        try:
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            result = conn.query(SQLConfigValue.confvalue).filter(SQLConfigValue.domain==self.domain).filter(SQLConfigValue.confkey==key).first()
            if result: # result = ('bar',)
                result = result[0]
        except Exception as e:
            result = None
            self.logger.error(f'{self.sess.id} Could not connect to config SQL database: {e.__class__.__name__}: {str(e)}')
        return result

    def get_domain_config_all(self):
        retval = {}
        try:
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            result = conn.query(SQLConfigValue).filter(SQLConfigValue.domain==self.domain).all()
            for row in result:
                retval[row.confkey] = row.confvalue
        except Exception as e:
            self.logger.error(f'{self.sess.id} Could not connect to config SQL database: {e.__class__.__name__}: {str(e)}')
        return retval
    
    def lint(self):
        try:
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            conn.execute(text('SELECT 1'))
            return True
        except Exception as e:
            print(f'Failed to connect to database: {e.__class__.__name__} {str(e)}')
            return False


class ConfigFileBackend(ConfigBackendInterface):
    """Read domain overrides directly from config, using ca_<domain> sections"""
    def __init__(self, config, section):
        super().__init__(config, section)
        self.domain_section = f'ca_{self.domain}'
        self.default_section = 'ca_default'
        
    def set_rcpt(self, recipient):
        super().set_rcpt(recipient)
        self.domain_section = f'ca_{self.domain}'

    def get_domain_config_value(self, key):
        value = None
        try:
            value = self.config.get(self.domain_section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            try:
                value = self.config.get(self.default_section, key)
            except configparser.NoSectionError:
                self.logger.warning(f'No config section {self.default_section}')
            except configparser.NoOptionError:
                self.logger.debug(f'No config key {key} section {self.default_section}')
        return value

    def get_domain_config_all(self):
        retval = {}
        try:
            # get values from default section
            for option in self.config.options(self.default_section):
                retval[option] = self.config.get(self.default_section, option)
        except configparser.NoSectionError:
            self.logger.warning(f'No config section {self.default_section}')
        try:
            # override with per domain values
            for option in self.config.options(self.domain_section):
                retval[option] = self.config.get(self.domain_section, option)
        except configparser.NoSectionError:
            self.logger.debug(f'No config section {self.domain_section}')
        return retval


class DBConfigBackend(ConfigFileBackend):
    def set_rcpt(self, recipient):
        super().set_rcpt(recipient)
        self.config = DBConfig(self.config, None)
        self.config.set_rcpt(recipient)

    # def get_domain_config_value(self, key):
    #    return self.config.get(self.section, key)

    # def get_domain_config_all(self):
    #    retval = {}
    #    self.config.load_section(self.section)
    #    data = self.config.sectioncache[self.section]
    #    for row in data:
    #        retval[row[0]] = row[1]
    #    return retval


class TagConfigBackend(ConfigBackendInterface):
    """
    read config values from session tags
    set a config like this:
    tag:filterconfig:${recipient}
    to match session tags like this:
    sess.tags = {'filterconfig': {'user@example.com':{'smtp_port':2525}}}
    """
    def get_domain_config_value(self, key):
        if self.sess is None:
            return None
        keylist = self.tagconfig.split(':')[1:]
        keylist.append(key)
        value = self.sess.tags.copy()
        for key in keylist:
            if key.startswith('$'):
                template = _SuspectTemplate(key)
                key = template.safe_substitute({'recipient': self.recipient, 'domain': self.domain})
            value = value.get(key, {})
        return value or None
    
    def get_domain_config_all(self):
        if self.sess is None:
            self.logger.warning('session not initialised')
            return {}
        keylist = self.tagconfig.split(':')[1:]
        value = self.sess.tags.copy()
        for key in keylist:
            if key.startswith('$'):
                template = _SuspectTemplate(key)
                key = template.safe_substitute({'recipient': self.recipient, 'domain': self.domain})
            value = value.get(key, {})
        return value


class MockSession:
    id = 'cmd'
    tags = {}
    def get_templ_dict(self):
        return {}

class SMTPTestCommandLineInterface(BackendMixin):
    def __init__(self):
        super().__init__()
        self.section = 'AddressCheck'

        self.commandlist = {
            'put-address': self.put_address,
            'wipe-address': self.wipe_address,
            'wipe-domain': self.wipe_domain,
            'cleanup': self.cleanup,
            'test-dry': self.test_dry,
            'test-config': self.test_config,
            'update': self.update,
            'help': self.help,
            'show-domain': self.show_domain,
            'devshell': self.devshell,
            'show-skiplist': self.show_skiplist,
            'unskiplist': self.unskiplist,
            'init-database': self.init_db,
        }

    async def cleanup(self, *args):
        config = get_config()
        self._init_cache(config, self.section)
        poscount, negcount, blcount = await self.cache.cleanup()
        if 'verbose' in args:
            print(f"Removed {poscount} positive, {negcount} negative records from history data")
            print(f"Removed {blcount} expired relays from call-ahead skiplist")

    def devshell(self, *args):
        """Drop into a python shell for debugging"""
        # noinspection PyUnresolvedReferences,PyCompatibility
        import readline
        import code
        logging.basicConfig(level=logging.DEBUG)
        cli = self
        config = get_config('../../../conf/fuglu.conf.dist', '../../../conf/conf.d')
        config.read('../../../conf/conf.d/call-ahead.conf.dist')
        self._init_cache(config, self.section)
        plugin = AddressCheck(config)
        print("cli : Command line interface class")
        print("sqlcache : SQL cache backend")
        print("plugin: AddressCheck Plugin")
        terp = code.InteractiveConsole(locals())
        terp.interact("")

    def help(self, *args):
        myself = sys.argv[0]
        print("usage:")
        print(f"{myself} <command> [args]")
        print("")
        print("Available commands:")
        commands = [
            ("test-dry", "<server> <emailaddress> [<emailaddress>] [<emailaddress>]",
             "test recipients on target server using the null-sender, does not use any config or caching data"),
            ("test-config", "<emailaddress>", "test configuration using targetaddress <emailaddress>. shows relay lookup and target server information"),
            ("update", "<emailaddress>", "test & update server state&address cache for <emailaddress>"),
            ("put-address", "<emailaddress> <positive|negative> <ttl> <message>", "add <emailaddress> to the cache"),
            ("wipe-address", "<emailaddress>", "remove <emailaddress> from the cache/history"),
            ("wipe-domain", "<domain> [positive|negative|all (default)]", "remove positive/negative/all entries for domain <domain> from the cache/history"),
            ("show-domain", "<domain>", "list all cache entries for domain <domain>"),
            ("show-skiplist", "", "display all servers currently skiplisted for call-aheads"),
            ("unskiplist", "<relay or domain>", "remove relay from the call-ahead skiplist"),
            ("cleanup", "[verbose]", "clean history data from database. this can be run from cron. add 'verbose' to see how many records where cleared"),
            ("init-database", "", "creates database tables using dbconnection specified in config file"),
        ]
        for cmd, arg, desc in commands:
            self._print_help(cmd, arg, desc)

    def _print_help(self, command, args, description):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()
        bold = fc.MODE['bold']
        cyan = fc.FG['cyan']
        print("%s %s\t%s" % (fc.strcolor(command, [bold, ]), fc.strcolor(args, [cyan, ]), description))

    def performcommand(self):
        args = sys.argv
        if len(args) < 2:
            print("no command given.")
            self.help()
            sys.exit(1)

        cmd = args[1]
        cmdargs = args[2:]
        if cmd not in self.commandlist:
            print(f"command '{cmd}' not implemented. try ./call-ahead help")
            sys.exit(1)

        cmdfunc = self.commandlist[cmd]
        if asyncio.iscoroutinefunction(cmdfunc):
            event_loop = get_event_loop(self.section)
            event_loop.run_until_complete(cmdfunc(*cmdargs))
        else:
            cmdfunc(*cmdargs)

    async def test_dry(self, *args):
        if len(args) < 2:
            print("usage: test-dry <server> <address> [...<address>]")
            sys.exit(1)
        server = args[0]
        addrs = args[1:]
        test = SMTPTest(section=self.section, miltersession=MockSession()) # config is passed later

        domain = sm.MilterSession.extract_domain(addrs[0])
        try:
            config = get_config()
            test.config = config
            self._init_config_backend(addrs[0], config, self.section)
            domainconfig = self.config_backend.get_domain_config_all()
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
            except (ValueError, TypeError, KeyError, configparser.NoSectionError):
                timeout = 10
            try:
                use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
            except (ValueError, TypeError, KeyError, configparser.NoSectionError):
                use_tls = True
            try:
                smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
            except (ValueError, TypeError, KeyError, configparser.NoSectionError):
                smtp_port = smtplib.SMTP_PORT
        except IOError as e:
            print(str(e))
            timeout = 10
            use_tls = 1
            smtp_port = smtplib.SMTP_PORT

        result = await test.smtptest(server, addrs, timeout=timeout, use_tls=use_tls, port=smtp_port)
        print(result)

    async def test_config(self, *args):
        logging.basicConfig(level=logging.INFO)
        if len(args) != 1:
            print("usage: test-config <address>")
            sys.exit(1)
        address = args[0]

        domain = sm.MilterSession.extract_domain(address)

        config = get_config()
        self._init_config_backend(address, config, self.section)
        domainconfig = self.config_backend.get_domain_config_all()

        print("Checking address cache...")
        self._init_cache(config, self.section)
        entry = await self.cache.get_address(address)
        if entry is not None:
            positive, message = entry
            etp = "negative"
            if positive:
                etp = "positive"
            print(f"We have {etp} cache entry for {address}: {message}")
        else:
            print(f"No cache entry for {address}")

        test = SMTPTest(config, self.section, miltersession=MockSession())
        relays = await test.get_relays(domain, domainconfig)  # type: list
        if relays is None:
            print(f"No relay for domain {domain} found!")
            sys.exit(1)
        print(f"Relays for domain {domain} are {', '.join(relays)}")
        for relay in relays:
            print(f"Testing relay {relay}")
            if await self.cache.is_skiplisted(domain, relay):
                print(f"{relay} is currently skiplisted for call-aheads")
            else:
                print(f"{relay} not skiplisted for call-aheads")

            print("Checking if server supports verification....")

            sender = test.get_domain_config(domain, 'sender', domainconfig, {'bounce': '', 'originalfrom': ''})
            testaddress = test.maketestaddress(domain, domainconfig)
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
            except (ValueError, TypeError):
                timeout = 10
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
            try:
                smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
            except (ValueError, TypeError, KeyError, configparser.NoSectionError):
                smtp_port = smtplib.SMTP_PORT
            result = await test.smtptest(relay, [address, testaddress], mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)
            if result.state != SMTPTestResult.TEST_OK:
                print("There was a problem testing this server:")
                print(result)
                continue

            addrstate, code, msg = result.rcptoreplies[testaddress]
            if addrstate == SMTPTestResult.ADDRESS_OK:
                print("Server accepts any recipient")
            elif addrstate == SMTPTestResult.ADDRESS_TEMPFAIL:
                print("Temporary problem / greylisting detected")
            elif addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                print("Server supports recipient verification")

            print(result)

    async def put_address(self, *args):
        if len(args) < 4:
            print("usage: put-address <emailaddress> <positive|negative> <ttl> <message>")
            sys.exit(1)

        address = args[0]

        strpos = args[1].lower()
        assert strpos in ['positive', 'negative'], "Additional argument must be 'positive' or 'negative'"
        if strpos == 'positive':
            pos = True
        else:
            pos = False

        try:
            ttl = int(args[2])
        except (ValueError, TypeError):
            print('ttl must be an integer')
            sys.exit(1)

        message = ' '.join(args[3:])

        config = get_config()
        self._init_cache(config, self.section)
        await self.cache.put_address(address, ttl, pos, message, 'cmdline-static-add')

    async def wipe_address(self, *args):
        if len(args) != 1:
            print("usage: wipe-address <address>")
            sys.exit(1)
        config = get_config()
        self._init_cache(config, self.section)
        rowcount = await self.cache.wipe_address(args[0])
        print(f"Wiped {rowcount} records")

    async def wipe_domain(self, *args):
        if len(args) < 1:
            print("usage: wipe-domain <domain> [positive|negative|all (default)]")
            sys.exit(1)

        domain = args[0]

        pos = None
        strpos = ''
        if len(args) > 1:
            strpos = args[1].lower()
            assert strpos in ['positive', 'negative', 'all'], "Additional argument must be 'positive', 'negative' or 'all'"
            if strpos == 'positive':
                pos = True
            elif strpos == 'negative':
                pos = False
            else:
                pos = None
                strpos = ''

        config = get_config()
        self._init_cache(config, self.section)
        rowcount = await self.cache.wipe_domain(domain, pos)
        print(f"Wiped {rowcount} {strpos} records")

    async def show_domain(self, *args):
        if len(args) != 1:
            print("usage: show-domain <domain>")
            sys.exit(1)
        config = get_config()
        self._init_cache(config, self.section)
        domain = args[0]
        rows = await self.cache.get_all_addresses(domain)  # type: list

        print(f"Cache for domain {domain} (-: negative entry, +: positive entry)")
        for row in rows:
            email, positive = row
            if positive:
                print(f"+ {email}")
            else:
                print(f"- {email}")
        total = len(rows)
        print(f"Total {total} cache entries for domain {domain}")

    async def show_skiplist(self, *args):
        if len(args) > 0:
            print("usage: show-blackist")
            sys.exit(1)
        config = get_config()
        self._init_cache(config, self.section)
        rows = await self.cache.get_skiplist()  # type: list

        print("Call-ahead skiplist (domain/relay/reason/expiry):")
        for row in rows:
            domain, relay, reason, exp = row
            print(f"{domain}\t{relay}\t{reason}\t{exp}")

        total = len(rows)
        print(f"Total {total} skiplisted relays")

    async def unskiplist(self, *args):
        if len(args) < 1:
            print("usage: unskiplist <relay or domain>")
            sys.exit(1)
        relay = args[0]
        config = get_config()
        self._init_cache(config, self.section)
        count = await self.cache.unskiplist(relay)
        print(f"{count} entries removed from call-ahead skiplist")

    async def update(self, *args):
        logging.basicConfig(level=logging.INFO)
        if len(args) != 1:
            print("usage: update <address>")
            sys.exit(1)
        address = args[0]

        domain = sm.MilterSession.extract_domain(address)

        config = get_config()
        self._init_cache(config, self.section)
        self._init_config_backend(address, config, self.section)
        domainconfig = self.config_backend.get_domain_config_all()

        test = SMTPTest(config, self.section, miltersession=MockSession())
        relays = await test.get_relays(domain, domainconfig)
        if relays is None:
            print(f"No relay for domain {domain} found!")
            sys.exit(1)
        print(f"Relays for domain {domain} are {relays}")

        relay = relays[0]
        sender = test.get_domain_config(domain, 'sender', domainconfig, {'bounce': '', 'originalfrom': ''})
        testaddress = test.maketestaddress(domain, domainconfig)
        try:
            timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
        except (ValueError, TypeError, KeyError, configparser.NoSectionError):
            timeout = 10
        try:
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
        except (ValueError, TypeError, KeyError, configparser.NoSectionError):
            use_tls = True
        try:
            smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
        except (ValueError, TypeError, KeyError, configparser.NoSectionError):
            smtp_port = smtplib.SMTP_PORT

        result = await test.smtptest(relay, [address, testaddress], mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)

        try:
            servercachetime = test.get_domain_config_int(domain, 'test_server_interval', domainconfig)
        except ValueError:
            servercachetime = 3600
        if result.state != SMTPTestResult.TEST_OK:
            print("There was a problem testing this server:")
            print(result)
            print("putting server on skiplist")
            await self.cache.skiplist(domain, relay, servercachetime, result.stage, result.errormessage, 'cmdline-static-add')
            return

        addrstate, code, msg = result.rcptoreplies[testaddress]
        recverificationsupport = None
        if addrstate == SMTPTestResult.ADDRESS_OK:
            recverificationsupport = False
        elif addrstate == SMTPTestResult.ADDRESS_TEMPFAIL:
            recverificationsupport = False
        elif addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
            recverificationsupport = True

        if recverificationsupport:

            if await self.cache.is_skiplisted(domain, relay):
                print(f"Server {relay} for domain {domain} was skiplisted - removing from skiplist")
                await self.cache.unskiplist(relay)
                await self.cache.unskiplist(domain)

            addrstate, code, msg = result.rcptoreplies[address]
            if addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                positive = False
                cachetime = test.get_domain_config_int(domain, 'negative_cache_time', domainconfig, fallback=14400)
            else:
                positive = True
                cachetime = test.get_domain_config_int(domain, 'positive_cache_time', domainconfig, fallback=7*86400)

            await self.cache.put_address(address, cachetime, positive, msg, 'cmdline-update-add')
            neg = ""
            if not positive:
                neg = "negative"
            print(f"{neg} cached {address} for {cachetime} seconds")
        else:
            print("Server accepts any recipient")
            if config.getboolean('AddressCheck', 'always_assume_rec_verification_support', fallback=True):
                print("skiplistings disabled in config - not skiplisting")
            else:
                await self.cache.skiplist(domain, relay, servercachetime, result.stage, 'accepts any recipient')
                print("Server skiplisted")
    
    def init_db(self):
        config = get_config()
        dbconn = config.get(self.section, 'dbconnection', fallback='')
        if dbconn:
            session = get_session(dbconn)
            bind = session.get_bind(SQLSkiplist)
            metadata = SQLSkiplist.metadata
            bind.connect()
            metadata.create_all(bind, tables=[SQLSkiplist.__table__, SQLAddressCache.__table__, SQLConfigValue.__table__])
            session.flush()
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                session.commit()
            elif sql_alchemy_version == SQL_ALCHEMY_V1:
                session.remove()
        else:
            print('dbconnection not defined in configuration')
        


# Usage for checks/debugging (you might have to change location of plugin
# for your installation
#
# get help
# > python /path/to/plugin/call-ahead.py
# apply command
# > python /path/to/plugin/call-ahead.py test-config aaa@aaa.aa
if __name__ == '__main__':
    logging.basicConfig()
    testcli = SMTPTestCommandLineInterface()
    testcli.performcommand()
