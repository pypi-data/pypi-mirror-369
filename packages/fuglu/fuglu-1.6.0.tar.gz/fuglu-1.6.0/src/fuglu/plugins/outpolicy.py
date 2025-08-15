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
import asyncio
import os
import logging
import threading
import time
import typing as tp
from string import Template
import re
import datetime
from email import message_from_bytes
import email.utils
from fuglu.shared import strip_address, extract_domain, FileList, ScannerPlugin, DUNNO, REJECT, \
    apply_template, string_to_actioncode, actioncode_to_string, get_outgoing_helo, Suspect
from fuglu.bounce import Bounce
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.sql import get_session, text, SQL_EXTENSION_ENABLED, sql_alchemy_version, SQL_ALCHEMY_V2
from fuglu.extensions.aioredisext import AIORedisMixin, ENABLED as REDIS_ENABLED, ExpiringCounter, RETRY_ON_EXCS
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin, BMPHeaderMixin, BMPEOHMixin
from fuglu.lib.patchedemail import PatchedMessage
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.logtools import createPIDinfo
from .fuzor import FuzorMixin, FuzorDigest
from .call_ahead import RedisAddress

try:
    from domainmagic.mailaddr import strip_batv, decode_srs, email_normalise_ebl, domain_from_mail
    from domainmagic.rbl import RBLLookup
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    RBLLookup = None
    def email_normalise_ebl(address):
        return address.lower()

    def domain_from_mail(value, **kwargs):
        return value.rsplit('@', 1)[-1]
    DOMAINMAGIC_AVAILABLE = False

try:
    from pfqd.qstore import QStore
    from pfqd.qtools import queue_size, COL_FROM_DOM, COL_FROM_ADDR
    PFQD_AVAILABLE = True
except ImportError:
    PFQD_AVAILABLE = False


def get_login_from_suspect(suspect, sasl_hdr=None):
    login = suspect.milter_macros.get('auth_authen')
    if login is None and sasl_hdr is not None:
        login = suspect.get_header(sasl_hdr)
    return login


class SenderDomainRulesCache(object):
    def __init__(self, dbconnection=None, refreshtime=300):
        self._dbconnection = dbconnection
        self.refreshtime = refreshtime
        self.logger = logging.getLogger(f'fuglu.plugin.outpolicy.{self.__class__.__name__}')
        self.spoofing_cache = {}
        self.bounces_cache = {}
        self.domain_cache = {}
        self.lock = threading.Lock()
        if self._dbconnection is not None:
            self.logger.debug('db for refresh: %s' % self._dbconnection)
            self._refreshcache()
        else:
            self.logger.debug('no db connection')
        t = threading.Thread(target=self.reloadthread)
        t.daemon = True
        t.start()

    @property
    def dbconnection(self):
        return self._dbconnection

    @dbconnection.setter
    def dbconnection(self, dbconnection):
        if dbconnection is not None and self._dbconnection != dbconnection:
            self._dbconnection = dbconnection
            self._refreshcache()

    def reloadthread(self):
        self.logger.info(f'Reloader thread started. Reloading every {self.refreshtime} seconds')
        while True:
            time.sleep(self.refreshtime)
            if self.dbconnection is not None:
                self._refreshcache()

    def _refreshcache(self, attempts=3):
        self.logger.debug(f"Call refreshcache for {createPIDinfo()}")
        while attempts:
            attempts -= 1
            conn = None
            try:
                self.lock.acquire()
                try:
                    #conn = get_session(self.dbconnection)

                    conn = get_session(self.dbconnection)
                    query = 'SELECT account_name, allow_spoofing, allow_bounces FROM relay_account'
                    result = conn.execute(text(query))
                    accounts = result.fetchall()
                    spoofing_cache = {}
                    spoofing_count = 0
                    bounces_cache = {}
                    bounces_count = 0
                    for line in accounts:
                        key = line['account_name']
                        spoofing_cache[key] = bool(line['allow_spoofing'])
                        if spoofing_cache[key]:
                            spoofing_count += 1
                        bounces_cache[key] = bool(line['allow_bounces'])
                        if bounces_cache[key]:
                            bounces_count += 1
                    self.spoofing_cache = spoofing_cache
                    self.bounces_cache = bounces_cache
                    self.logger.info(f'Loaded {len(accounts)} accounts of which {spoofing_count} are allowed to spoof')
                    conn.close()

                    conn = get_session(self.dbconnection)
                    query = 'SELECT relay_account, domainname FROM relay_senderdomain'
                    result = conn.execute(text(query))
                    domain_cache = {}
                    domain_count = 0
                    senders = result.fetchall()
                    for line in senders:
                        key = line['relay_account']
                        value = line['domainname']
                        if key not in domain_cache:
                            domain_cache[key] = []
                        domain_cache[key].append(value)
                        domain_count += 1
                    self.domain_cache = domain_cache
                    self.logger.info(f'Loaded {len(domain_cache)} accounts and {domain_count} domains')
                    conn.close()

                    # success, no further attempts needed
                    attempts = 0
                except Exception as e:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    if attempts:
                        waitfor = abs(4-attempts)/4
                        self.logger.warning(f'Exception while reloading (retry in {waitfor}s): {e.__class__.__name__}: {str(e)}')
                        time.sleep(waitfor)
                    else:
                        self.logger.error(f'Exception for {createPIDinfo()} while reloading: {e.__class__.__name__}: {str(e)}', exc_info=e)
            finally:
                self.lock.release()

    def can_spoof(self, relay_account):
        value = self.spoofing_cache.get(relay_account)
        self.logger.debug(f'sasl_user: {relay_account} spoofing: {value}')
        return value

    def can_bounce(self, relay_account):
        value = self.bounces_cache.get(relay_account)
        self.logger.debug(f'sasl_user: {relay_account} bounces: {value}')
        return value

    def can_send(self, relay_account, sender_domain):
        domains = self.domain_cache.get(relay_account, [])
        return sender_domain in domains


class SenderDomainRules(BMPRCPTMixin, BasicMilterPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section=section)

        self.logger = self._logger()

        self.requiredvars = {
            'testmode': {
                'default': 'False',
                'description': 'set to true to only log. set to false to actually reject policy violations'
            },
            'dbconnection': {
                'default': '',
                'description': 'SQLAlchemy Connection string'
            },
            'rejectmessage': {
                'default': '${from_domain} is not in my list of allowed sender domains for account ${sasl_user}',
                'description': 'reject message template for policy violators'
            },
            'reloadinterval': {
                'default': '300',
                'description': 'Interval until listings are refreshed'
            },
            'bounceblock': {
                'default': 'True',
                'description': 'Block bounces for selected sasl users'
            },
            'allow_rcpt': {
                'default': '',
                'description': 'list of recipients and recipient domains that are always allowed to receive mail',
            },
            'wltagname': {
                'default': 'skipmplugins',
                'description': 'tagname in case of WL hit (empty: don\'t set, skipmplugins to skip milter plugins)'
            },
            'wltagvalue': {
                'default': '',
                'description': 'tag content in case of WL hit (empty: don\'t set)'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
        self._cache = None

    @property
    def cache(self):
        # create rules cache only when required
        if self._cache is None:
            self._cache = SenderDomainRulesCache(self.config.get(self.section, 'dbconnection'))
        return self._cache

    def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state:
            # not active in current state
            return True

        fc = FunkyConsole()

        if not self.check_config():
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        try:
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            conn.execute('SELECT 1')
        except Exception as e:
            print(fc.strcolor('ERROR: ', "red"), f'DB Connection failed. Reason: {str(e)}')
            return False

        self.cache.dbconnection = self.config.get(self.section, 'dbconnection')
        print(f'cached {len(self.cache.spoofing_cache)} spoofing entries '
              f'and {len(self.cache.domain_cache)} domain entries')
        return True

    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        try:
            recipient = force_uString(recipient)
            if recipient is not None:
                to_address = strip_address(recipient)
                to_domain = extract_domain(to_address)
            else:
                to_address = None
                to_domain = None

            sender = force_uString(sess.sender)
            if sender is not None:
                if DOMAINMAGIC_AVAILABLE:
                    from_address = strip_batv(strip_address(sender))
                    from_address = decode_srs(from_address)
                else:
                    from_address = sender
                from_domain = extract_domain(from_address)
            else:
                from_address = None
                from_domain = None

            sasl_user = force_uString(sess.sasl_user)

            # don't query locally generated messages
            if sasl_user is None or str(sasl_user).strip() == '':
                self.logger.debug(f'{sess.id} no sasl user -> continue')
                return sm.CONTINUE

            if from_domain is None or from_domain.strip() == '':
                # bounce
                if self.config.getboolean(self.section, 'bounceblock') and not self.cache.can_bounce(sasl_user):
                    return sm.REJECT, 'Bounce denied'
                else:
                    self.logger.debug(f'{sess.id} no from domain -> continue')
                    return sm.CONTINUE

            fields = sess.get_templ_dict()

            # always allow spoofing to certain recipients
            allow_rcpt = self.config.getlist(self.section, 'allow_rcpt')
            if to_domain in allow_rcpt or to_address in allow_rcpt:
                self.logger.info(f'{sess.id} sasl_user={sasl_user}, spoofing allowed to allowed mailbox {to_address}')
                # tag and continue (if possible)
                wltag = self.config.get(self.section, 'wltagvalue')
                wlname = self.config.get(self.section, 'wltagname')
                if wlname and wltag:
                    if wlname in sess.tags:
                        # append if already present
                        sess.tags[wlname] = f"{sess.tags[wlname]},{wltag}"
                    else:
                        # set tag
                        sess.tags[wlname] = wltag
                elif wlname:
                    self.logger.warning(f"{sess.id} allowed recipient: tag name defined but no value")
                elif wltag:
                    self.logger.error(f"{sess.id} allowed recipient: no tag name defined but value")
                else:
                    self.logger.info(f"{sess.id} allowed recipient: no tag no value defined -> accept mail")
                    return sm.ACCEPT

                return sm.CONTINUE

            self.cache.refreshtime = self.config.getint(self.section, 'reloadinterval')
            self.cache.dbconnection = self.config.get(self.section, 'dbconnection')

            # check if account is allowed to spoof any domain
            spoofing_allowed = self.cache.can_spoof(sasl_user)

            if spoofing_allowed is None:
                # no row found
                self.logger.warning(f'{sess.id} No relay config found for sasl_user={sasl_user}')
                return sm.TEMPFAIL, f'could not load configuration for user {sasl_user}'

            elif spoofing_allowed:
                self.logger.debug(f'{sess.id} sasl_user={sasl_user}, spoofing allowed, accepting sender domain')
                return sm.CONTINUE

            # check if senderdomain is in allowlist
            domain_found = self.cache.can_send(sasl_user, from_domain)  # returns True or False
            if domain_found:
                self.logger.debug(f'{sess.id} sasl_user={sasl_user} sender domain {from_domain} is in allow list.')
            else:
                self.logger.warning(f'{sess.id} Domain spoof: sasl_user={sasl_user} from={from_address} to={to_address}')
                testmode = self.config.getboolean(self.section, 'testmode')
                rejstring = self.config.get(self.section, 'rejectmessage')
                tmpl = Template(rejstring)
                rejectmessage = tmpl.safe_substitute(fields)
                if testmode:
                    self.logger.warning(f'{sess.id} Testmode (warn only): {rejectmessage}')
                else:
                    self.logger.debug(f'{sess.id} sasl_user={sasl_user}, reject with message: {rejectmessage}')
                    return sm.REJECT, rejectmessage

        except Exception as e:
            self.logger.error(f'{sess.id} Senderdomain plugin failed : {str(e)}')

        self.logger.debug(f'{sess.id} return continue')
        return sm.CONTINUE


class NoBounce(BMPRCPTMixin, BasicMilterPlugin):
    """
    do not send bounces to certain recipient domains (e.g. to prevent listing on backscatter rbls)
    """

    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.nobounce = None
        self.nobounce_mx = None

        self.requiredvars = {
            'nobouncefile': {
                'default': '${confdir}/nobounce.txt',
                'description': 'list of domains to which bounces will be disallowed'
            },
            'nobounce_mx_file': {
                'default': '${confdir}/nobounce_mx.txt',
                'description': 'list of mx hosts to which bounces will be disallowed (requires DNSData mx lookup on recipient)'
            },
            'rejectmessage': {
                'default': '${to_domain} does not accept bounces',
                'description': 'reject message template for policy violators'
            },
            'rejectmessage_mx': {
                'default': '${to_domain}\'s MX ${mx} does not accept bounces',
                'description': 'reject message template for policy violators due to uncooperative mx'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def _init_lists(self):
        if self.nobounce is None:
            nobouncefile = self.config.get(self.section, 'nobouncefile')
            if nobouncefile and os.path.exists(nobouncefile):
                self.nobounce = FileList(nobouncefile)

        if self.nobounce_mx is None:
            nobounce_mx_file = self.config.get(self.section, 'nobounce_mx_file')
            if nobounce_mx_file and os.path.exists(nobounce_mx_file):
                self.nobounce_mx = FileList(nobounce_mx_file, lowercase=True)

    def _check_nobounce_mx(self, sess, rcpt_domain):
        if self.nobounce_mx is not None:
            mxrecs = sess.tags.get(f'dnsdata.recipient.{rcpt_domain.lower()}', {}).get('MX', [])
            nobounce_mx = set(self.nobounce_mx.get_list())
            for mxrec in mxrecs:
                if mxrec.lower() in nobounce_mx:
                    return mxrec
        return None

    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) \
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        sender = force_uString(sess.sender)

        if sender is None or sender == '':
            self._init_lists()

            to_address = force_uString(recipient)
            to_address = strip_address(to_address)
            to_domain = extract_domain(to_address)

            if self.nobounce is not None:
                nobounce = set(self.nobounce.get_list())
                if to_domain in nobounce:
                    rejstring = self.config.get(self.section, 'rejectmessage')
                    tmpl = Template(rejstring)
                    fields = sess.get_templ_dict()
                    fields['to_domain'] = to_domain
                    rejectmessage = tmpl.safe_substitute(fields)
                    return sm.REJECT, rejectmessage

            nobounce_mx = self._check_nobounce_mx(sess, to_domain)
            if nobounce_mx is not None:
                rejstring = self.config.get(self.section, 'rejectmessage_mx')
                tmpl = Template(rejstring)
                fields = sess.get_templ_dict()
                fields['mx'] = nobounce_mx
                fields['to_domain'] = to_domain
                rejectmessage = tmpl.safe_substitute(fields)
                return sm.REJECT, rejectmessage

        return sm.CONTINUE

    def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole

        if state and state not in self.state:
            # not active in current state
            return True

        fc = FunkyConsole()

        if not self.check_config():
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        nobouncefile = self.config.get(self.section, 'nobouncefile')
        if nobouncefile and not os.path.exists(nobouncefile):
            print(fc.strcolor('ERROR: ', "red"), f'nobouncefile {nobouncefile} does not exist')
            return False

        nobouncefile_mx = self.config.get(self.section, 'nobounce_mx_file')
        if nobouncefile_mx and not os.path.exists(nobouncefile_mx):
            print(fc.strcolor('ERROR: ', "red"), f'nobounce_mx_file {nobouncefile_mx} does not exist')
            return False

        self._init_lists()
        if nobouncefile and self.nobounce is None:
            print(fc.strcolor('ERROR: ', "red"), 'failed to initialise no bounce list')
            return False

        if nobouncefile_mx and self.nobounce_mx is None:
            print(fc.strcolor('ERROR: ', "red"), 'failed to initialise no bounce MX list')
            return False

        return True


class MilterData2Header(ScannerPlugin):
    """
    Save specific postfix environment data in a header.
    Currently only supports saving sasl login username.
    Run this plugin in a milter mode fuglu to read data in e.g. a subsequently running after queue fuglu.
    Consider removing headers after reinjection into postfix.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },
        }

    def examine(self, suspect):
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        login = suspect.milter_macros.get('auth_authen')
        suspect.add_header(sasl_hdr, login)
        return DUNNO


class TrapIntercept(AIORedisMixin, ScannerPlugin):
    """
    This plugin intercepts mail to known trap recipients.
    A copy of the sent mail is bounced to a report address, mail is rejected and the sending account will be blocked.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'traps_file': {
                'default': '${confdir}/traps.txt',
                'description': 'file with known traps'
            },

            'trap_regex': {
                'default': '',
                'description': 'regex to match traps by pattern'
            },

            'traps_mx_file': {
                'default': '${confdir}/traps_mx.txt',
                'description': 'file with known traps MX (requires DNSData MX lookup on recipient)'
            },

            'traps_mxa_file': {
                'default': '${confdir}/traps_mxa.txt',
                'description': 'file with IPs of known traps MX (requires DNSData MXA lookup on recipient)'
            },

            'sender_exceptions_file': {
                'default': '${confdir}/trap_sender_exceptions.txt',
                'description': 'file with permitted senders (no block, no reject)'
            },
            
            'sender_rejectonly_file': {
                'default': '${confdir}/trap_sender_noreject.txt',
                'description': 'file with senders that should not be blocked (only reject)'
            },

            'rcpt_exceptions_regex': {
                'default': '^([a-z]{0,6}support|helpdesk|it|edv|abuse|postmaster)@',
                'description': 'regex with permitted recipients (e.g. support and helpdesk). regex is case insensitive.'
            },

            'actioncode': {
                'default': 'REJECT',
                'description': "plugin action if policy is violated",
            },

            'rejectmessage': {
                'default': 'this account is sending spam - please contact your IT support',
                'description': 'reject/defer message template for policy violators. supports variable "culprit" which contains the trap address'
            },

            'dbconnection': {
                'default': '',
                'description': 'sqlalchemy db connection string mysql://user:pass@host/database?charset=utf-8',
            },

            'sql_stmt_block': {
                'default': """
                    INSERT INTO relay_senderaccess (pattern, action, message, comment, relay_account, active)
                    VALUES (:sender, :action, :message, :comment, :relay_account, 1)
                    ON DUPLICATE KEY UPDATE edited=now(), active=1, comment=concat(comment, '\n', :comment);
                    """,
                'description': 'sql query to enable block'
            },
            
            'sql_stmt_reject': {
                'default': """SELECT action, message FROM relay_senderaccess WHERE pattern=:sender and active=1;""",
                'description': 'sql query to apply block'
            },

            'redis_timeout': {
                'default': '2',
                'description': 'redis backend timeout in seconds',
            },
            
            'redis_ttl': {
                'default': '0',
                'description': 'redis backend block ttl in seconds',
            },

            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },

            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },

            'report_recipient': {
                'default': '',
                'description': 'address of report recipient.',
            },

            'subject_template': {
                'default': 'Spam suspect from ${from_address}',
                'description': 'template of subject line of report mail',
            },

            'account_uri_template': {
                'default': '',
                'description': 'template of URI to sender account details',
            },

            'search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results',
            },
            
            'blocklistconfig': {
                'default': '${confdir}/rbltraps.conf',
                'description': 'Domainmagic RBL lookup config file',
            },
            
            'no_delist_before': {
                'default': str(86400*3),
                'description': 'do not allow delisting before this much time after listing passed.'
            }

        }

        self.traps = None
        self.traps_mx = None
        self.traps_mxa = None
        self.sender_exceptions = None
        self.sender_rejectonly = None
        self.rbllookup = None
        self.rgx_cache = {}

    def _init_lists(self):
        if self.traps is None:
            traps_file = self.config.get(self.section, 'traps_file')
            if traps_file and os.path.exists(traps_file):
                self.traps = FileList(traps_file, additional_filters=email_normalise_ebl)

        if self.traps_mx is None:
            traps_mx_file = self.config.get(self.section, 'traps_mx_file')
            if traps_mx_file and os.path.exists(traps_mx_file):
                self.traps_mx = FileList(traps_mx_file)

        if self.traps_mxa is None:
            traps_mxa_file = self.config.get(self.section, 'traps_mxa_file')
            if traps_mxa_file and os.path.exists(traps_mxa_file):
                self.traps_mxa = FileList(traps_mxa_file)

        if self.sender_exceptions is None:
            sender_exceptions_file = self.config.get(self.section, 'sender_exceptions_file')
            if sender_exceptions_file and os.path.exists(sender_exceptions_file):
                self.sender_exceptions = FileList(sender_exceptions_file, additional_filters=email_normalise_ebl)
        
        if self.sender_rejectonly is None:
            sender_rejectonly_file = self.config.get(self.section, 'sender_rejectonly_file')
            if sender_rejectonly_file and os.path.exists(sender_rejectonly_file):
                self.sender_rejectonly = FileList(sender_rejectonly_file, additional_filters=email_normalise_ebl)
                
        if self.rbllookup is None and RBLLookup is not None:
            blocklistconfig = self.config.get(self.section, 'blocklistconfig')
            if blocklistconfig and os.path.exists(blocklistconfig):
                self.rbllookup = RBLLookup()
                self.rbllookup.from_config(blocklistconfig)

    def _static_traps(self, rcpt):
        is_trap = False
        trap_regex = self.config.get(self.section, 'trap_regex')
        if trap_regex:
            if trap_regex not in self.rgx_cache:
                rgx = re.compile(trap_regex, re.I)
                self.rgx_cache[trap_regex] = rgx
            else:
                rgx = self.rgx_cache[trap_regex]
            if rgx.search(rcpt):
                is_trap = True
        return is_trap

    def _check_trap_mx(self, suspect, rcpt_domain):
        if self.traps_mx is not None:
            mxrecs = suspect.get_tag(f'dnsdata.recipient.{rcpt_domain}', {}).get('MX', [])
            trap_mx = set(self.traps_mx.get_list())
            for mxrec in mxrecs:
                if mxrec in trap_mx:
                    return True
        if self.traps_mxa is not None:
            mxarecs = suspect.get_tag(f'dnsdata.recipient.{rcpt_domain}', {}).get('MXA', [])
            trap_mxa = set(self.traps_mxa.get_list())
            for mxarec in mxarecs:
                if mxarec in trap_mxa:
                    return True
        return False
    
    def _check_trap_rbl(self, suspect, rcpt):
        if self.rbllookup is not None:
            listings = self.rbllookup.listings(rcpt)
            for identifier, humanreadable in iter(listings.items()):
                self.logger.debug(f'{suspect.id} {rcpt} listed in {identifier} {humanreadable}')
            if listings:
                return True
        return False
        

    async def examine(self, suspect):
        actioncode, message = await self._reject_sender(suspect)
        if message is not None:
            return actioncode, message

        self._init_lists()
        from_address = email_normalise_ebl(suspect.from_address)
        if self.sender_exceptions is not None:
            exceptions = set(self.sender_exceptions.get_list())
            if from_address in exceptions or suspect.from_domain.lower() in exceptions:
                self.logger.debug(f'{suspect.id} sender {suspect.from_address} is on exception list')
                return DUNNO
        
        if self.sender_rejectonly is not None:
            sender_rejectonly = set(self.sender_rejectonly.get_list())
        else:
            sender_rejectonly = {}

        if self.traps is not None:
            traps = set(self.traps.get_list())
        else:
            traps = {}
        
        for recipient in suspect.recipients:
            rcpt = email_normalise_ebl(recipient)
            rcpt_domain = domain_from_mail(recipient)
            if self._static_traps(rcpt) or self._check_trap_mx(suspect, rcpt_domain) \
                    or self._check_trap_rbl(suspect, rcpt) \
                    or rcpt in traps or rcpt_domain in traps:
                self.logger.warning(f'{suspect.id} sender={suspect.from_address} hit trap {rcpt}')
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {'culprit': rcpt})
                if from_address \
                        and from_address not in sender_rejectonly \
                        and suspect.from_domain.lower() not in sender_rejectonly \
                        and (SQL_EXTENSION_ENABLED or REDIS_ENABLED):
                    try:
                        await self._block_sender(suspect, rcpt, message)
                    except Exception as e:
                        self.logger.error(f'{suspect.id} failed to block sender {from_address} due to {e.__class__.__name__}: {str(e)}')
                else:
                    self.logger.debug(f'{suspect.id} not blocking sender. from_address={from_address} addr_rejectonly={from_address not in sender_rejectonly} dom_rejectonly={suspect.from_domain.lower() not in sender_rejectonly} sql={SQL_EXTENSION_ENABLED} redis={REDIS_ENABLED}')
                try:
                    self._send_mail(suspect, rcpt)
                except Exception as e:
                    reportto = self.config.get(self.section, 'report_recipient')
                    self.logger.error(f'{suspect.id} failed to send trapintercept mail to {reportto} due to {e.__class__.__name__}: {str(e)}')

                actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
                if actioncode == DUNNO:
                    message = None
                return actioncode, message
        return DUNNO

    async def lint(self):
        if not self.check_config():
            print('ERROR: config error')
            return False

        allowed_rcpts = self.config.get(self.section, 'rcpt_exceptions_regex')
        if allowed_rcpts:
            try:
                re.compile(allowed_rcpts, re.I)
            except Exception as e:
                print(f'ERROR: invalid rcpt_exceptions_regex {allowed_rcpts} compilation failed: {e.__class__.__name__}: {str(e)}')
                return False
        
        traps_rgx = self.config.get(self.section, 'trap_regex')
        if traps_rgx:
            try:
                re.compile(traps_rgx, re.I)
            except Exception as e:
                print(f'ERROR: invalid traps_regex {traps_rgx} compilation failed: {e.__class__.__name__}: {str(e)}')
                return False

        traps_file = self.config.get(self.section, 'traps_file')
        if traps_file and not os.path.exists(traps_file):
            print(f'ERROR: cannot find traps_file {traps_file}')
            return False

        traps_mx_file = self.config.get(self.section, 'traps_mx_file')
        if traps_mx_file and not os.path.exists(traps_mx_file):
            print(f'ERROR: cannot find traps_mx_file {traps_mx_file}')
            return False

        traps_mxa_file = self.config.get(self.section, 'traps_mxa_file')
        if traps_mxa_file and not os.path.exists(traps_mxa_file):
            print(f'ERROR: cannot find traps_mxa_file {traps_mxa_file}')
            return False

        exceptions_file = self.config.get(self.section, 'sender_exceptions_file')
        if exceptions_file and not os.path.exists(exceptions_file):
            print(f'ERROR: cannot find sender_exceptions_file {exceptions_file}')
            return False

        rejectonly_file = self.config.get(self.section, 'sender_rejectonly_file')
        if rejectonly_file and not os.path.exists(rejectonly_file):
            print(f'ERROR: cannot find sender_rejectonly_file {rejectonly_file}')
            return False
        
        blocklistconfig = self.config.get(self.section, 'blocklistconfig')
        if blocklistconfig and not os.path.exists(blocklistconfig):
            print(f'ERROR: cannot find blocklistconfig file {blocklistconfig}')
            return False
        if blocklistconfig and RBLLookup is None:
            print(f'ERROR: blocklistconfig is enabled but dependency domainmagic is missing')
            return False

        self._init_lists()
        if traps_file and self.traps is None:
            print(f'ERROR: failed to initialise traps from file {traps_file}')
            return False

        if traps_mx_file and self.traps_mx is None:
            print(f'ERROR: failed to initialise traps MX from file {traps_mx_file}')
            return False

        if traps_mxa_file and self.traps_mxa is None:
            print(f'ERROR: failed to initialise traps MXA from file {traps_mxa_file}')
            return False

        if exceptions_file and self.sender_exceptions is None:
            print(f'ERROR: failed to initialise exceptions list from file {exceptions_file}')
            return False
        
        if rejectonly_file and self.sender_rejectonly is None:
            print(f'ERROR: failed to initialise rejectonly list from file {rejectonly_file}')
            return False

        dbconnectstring = self.config.get(self.section, 'dbconnection')
        if not dbconnectstring:
            print('INFO: not using SQL backend')
        else:
            if not SQL_EXTENSION_ENABLED:
                print('WARNING: SQL extension not enabled, not using SQL database')
                return False

            try:
                dbsession = get_session(dbconnectstring)
                dbsession.execute('SELECT 1')
            except Exception as e:
                print('ERROR: failed to connect to SQL database: %s' % str(e))
                return False

        redis_url = self.config.get(self.section, 'redis_conn')
        if not redis_url:
            print('INFO: not using Redis backend')
        else:
            reply = await self.aioredisbackend.ping()
            if not reply:
                print(f'ERROR cannot ping redis server {redis_url}')
                return False
        return True

    async def _block_sender(self, suspect, culprit, message):
        blocked = None
        dbconnectstring = self.config.get(self.section, 'dbconnection')
        if dbconnectstring:
            blocked = self._block_sender_sql(suspect, culprit, message, dbconnectstring)

        redis_url = self.config.get(self.section, 'redis_conn')
        if redis_url:
            blocked = await self._block_sender_redis(suspect, culprit, message)

        if blocked is None:
            self.logger.warning(f'{suspect.id} no valid user block mechanism found')
            blocked = False
        return blocked

    def _block_sender_sql(self, suspect, culprit, message, dbconnectstring):
        dbsession = get_session(dbconnectstring)

        sql_stmt_block = self.config.get(self.section, 'sql_stmt_block')
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        no_delist_before = self.config.getint(self.section, 'no_delist_before')
        no_delist_ts = datetime.datetime.now() + datetime.timedelta(seconds=no_delist_before)
        sender = email_normalise_ebl(suspect.from_address)

        valdict = {
            'sender': sender,
            'action': self.config.get(self.section, 'actioncode'),
            'message': message,
            'comment': f'fugluid={suspect.id} rcpt={culprit}',
            'relay_account': get_login_from_suspect(suspect, sasl_hdr),
            'no_delist': False,
            'no_delist_before': no_delist_ts.isoformat(sep=' ', timespec='seconds') if no_delist_before > 0 else ''
        }

        rowcount = 0
        try:
            result = dbsession.execute(text(sql_stmt_block), valdict)
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                dbsession.commit()
            rowcount = result.rowcount
        except Exception as e:
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                dbsession.rollback()
            self.logger.error(f'{suspect.id} failed to block sender {sender} due to sql error: {e.__class__.__name__}: {str(e)}')
        finally:
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                dbsession.close()

        if rowcount == 1:
            self.logger.debug(f'{suspect.id} blocked {sender} in sql db')
            return True
        elif rowcount == 0:
            self.logger.warning(f'{suspect.id} tried to block {sender} but nothing was updated in sql db')
            return False
        else:
            self.logger.warning(f'{suspect.id} tried to block {sender} but more than one record was updated in sql db')
            return False

    async def _block_sender_redis(self, suspect, culprit, message):
        """
        call-ahead style redis backend
        """
        name = f'outblock-{email_normalise_ebl(suspect.from_address)}'
        comment = f'fugluid={suspect.id} rcpt={culprit}'
        values = RedisAddress(suspect.from_address, False, message, comment, suspect.id)
        values.data['no_delist'] = str(False)
        no_delist_before = self.config.getint(self.section, 'no_delist_before')
        no_delist_ts = datetime.datetime.now() + datetime.timedelta(seconds=no_delist_before)
        values.data['no_delist_before'] = no_delist_ts.isoformat(sep=' ', timespec='seconds') if no_delist_before > 0 else ''
        ttl = self.config.getint(self.section, 'redis_ttl', fallback=0) or None
        timeout = self.config.getint(self.section, 'redis_timeout', fallback=3)
        try:
            await self.aioredisbackend.hset(name.encode(), mapping=values.data, ttl=ttl, timeout=timeout)
            self.logger.debug(f'{suspect.id} blocked {suspect.from_address} in redis')
            return True
        except Exception as e:
            self.logger.warning(f'{suspect.id} failed to block {suspect.from_address} in redis due to {e.__class__.__name__}: {str(e)}')
            return False

    async def _reject_sender(self, suspect):
        actioncode = DUNNO
        message = None

        allowed_rcpts = self.config.get(self.section, 'rcpt_exceptions_regex')
        if allowed_rcpts and len(suspect.recipients) == 1:
            if allowed_rcpts in self.rgx_cache:
                rcpt_exceptions_regex = self.rgx_cache[allowed_rcpts]
            else:
                rcpt_exceptions_regex = re.compile(allowed_rcpts, re.I)
                self.rgx_cache = {allowed_rcpts: rcpt_exceptions_regex}
            if rcpt_exceptions_regex.search(suspect.to_address):
                self.logger.debug(f'{suspect.id} recipient {suspect.to_address} matches recipients exceptions regex')
                return actioncode, message # DUNNO, None
        elif not allowed_rcpts:
            self.logger.debug(f'{suspect.id} no recipients exceptions regex defined')
        elif len(suspect.recipients) > 1:
            self.logger.debug(f'{suspect.id} no rcpt permission check due to multiple recipients')
        
        dbconnectstring = self.config.get(self.section, 'dbconnection')
        if dbconnectstring:
            actioncode, message = self._reject_sender_sql(suspect, dbconnectstring)

        redis_url = self.config.get(self.section, 'redis_conn')
        if redis_url:
            message = await self._reject_sender_redis(suspect)
            if message is not None:
                actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
        return actioncode, message
    
    def _reject_sender_sql(self, suspect, dbconnectstring):
        actioncode = DUNNO
        message = None
        dbsession = get_session(dbconnectstring)
        sql_stmt_block = self.config.get(self.section, 'sql_stmt_block')
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        sender = email_normalise_ebl(suspect.from_address)
        
        valdict = {
            'sender': sender,
            'relay_account': get_login_from_suspect(suspect, sasl_hdr),
        }
        try:
            result = dbsession.execute(text(sql_stmt_block), valdict).first()
            if result:
                actioncode = actioncode_to_string(result.action)
                message = result.message
        except Exception as e:
            self.logger.error(f'{suspect.id} failed to query sender {sender} due to sql error: {e.__class__.__name__}: {str(e)}')
        finally:
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                dbsession.close()
        return actioncode, message

    async def _reject_sender_redis(self, suspect):
        message = None
        name = f'outblock-{email_normalise_ebl(suspect.from_address)}'
        timeout = self.config.getint(self.section, 'redis_timeout', fallback=3)
        try:
            entry = await self.aioredisbackend.hmget(name.encode(), ['message'], timeout=timeout)
            if entry is not None and entry[0] is not None:
                message = force_uString(entry[0])
        except Exception as e:
            self.logger.warning(f'{suspect.id} failed to get {suspect.from_address} info from redis due to {e.__class__.__name__}: {str(e)}')
        return message

    def _send_mail(self, suspect, culprit):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info(f'{suspect.id} not reported because report recipient is not defined')
            return

        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        login = get_login_from_suspect(suspect, sasl_hdr)
        tmpldata = {'sasl_login': login, 'culprit': culprit}
        account_uri = apply_template(self.config.get(self.section, 'account_uri_template'), suspect, tmpldata)
        search_uri = apply_template(self.config.get(self.section, 'search_uri_template'), suspect, tmpldata)
        
        subject = suspect.decode_msg_header(suspect.get_header('subject', ''), logid=suspect.id)

        body = f'Sender: {suspect.from_address}\n'
        body += f'Trap Recipient: {culprit}\n'
        body += f'Suspect ID: {suspect.id}\n'
        body += f'Subject: {subject}\n'
        if account_uri:
            body += f'Account: {account_uri}\n'
        if search_uri:
            body += f'Search: {search_uri}'

        subject = apply_template(self.config.get(self.section, 'subject_template'), suspect, tmpldata)
        msg = suspect.wrap(reporter, reportto, subject, body, 'spam.eml', self.config)

        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info(f'{suspect.id} Spam Suspect mail sent to {reportto} with queueid {queueid} for sender {suspect.from_address} and trap hit {culprit}')


class FuzorRateLimit(FuzorMixin, ScannerPlugin):
    """
    This plugin checks fuzor checksum of mail against redis database.
    if threshold is exceeded, a copy of the mail will be bounced to
    report address and all future mail is deferred until fuzor count
    is below threshold again.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'threshold': {
                'default': '100',
                'description': 'alert threshold'
            },
            'sender_exceptions_file': {
                'default': '',
                'description': 'file with senders that have a free pass to bulk'
            },
            'alert_exceptions_file': {
                'default': '',
                'description': 'file with senders that do not trigger an alert when bulking (but still get rate limited)'
            },
            'demomode': {
                'default': 'False',
                'description': 'if set to True: do not block (defer), only alert'
            },
            'actioncode': {
                'default': 'DEFER',
                'description': "plugin action if if policy is violated",
            },
            'rejectmessage': {
                'default': 'rate limit exceeded',
                'description': 'reject/defer message template for policy violators'
            },
            'subject_ignore_keys': {
                'default': '',
                'description': 'comma separated list of keys in subject to ignore messages (case insensitive)'
            },
            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },
            'report_recipient': {
                'default': '',
                'description': 'address of report recipient.',
            },
            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },
            'subject_template': {
                'default': 'Bulk suspect from ${from_address}',
                'description': 'template of URI to sender account details',
            },
            'account_uri_template': {
                'default': '',
                'description': 'template of URI to sender account details',
            },
            'search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results',
            },
            'rate_limit_none_digest': {
                'default': 'False',
                'description': 'apply rate limits even if no fuzor digest could be calculated',
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
        })

        self.sender_exceptions = None
        self.alert_exceptions = None
        try:
            self.subjectkeys = [k.lower().strip() for k in self.config.get(self.section, 'subject_ignore_keys').split(",")]
            # remove entries with empty strings
            self.subjectkeys = [k for k in self.subjectkeys if k]
        except Exception:
            self.subjectkeys = []

    async def lint(self):
        if not self.check_config():
            print('ERROR: config error')
            return False

        if not await FuzorMixin.lint(self):
            return False

        sender_exception_file = self.config.get(self.section, 'sender_exceptions_file')
        if sender_exception_file and not os.path.exists(sender_exception_file):
            print('ERROR: cannot find sender_exceptions_file %s' % sender_exception_file)
            return False

        alert_exception_file = self.config.get(self.section, 'alert_exception_file')
        if alert_exception_file and not os.path.exists(alert_exception_file):
            print('ERROR: cannot find alert_exceptions_file %s' % alert_exception_file)
            return False

        self._init_lists()
        if sender_exception_file and self.sender_exceptions is None:
            print('ERROR: failed to initialise sender_exceptions')
            return False

        try:
            self._init_backend()
            if self.backend is None:
                print('ERROR: backend not initiated')
                return False
        except Exception as e:
            print('ERROR failed to init backend: %s' % str(e))
            return False

        return True

    def _init_lists(self):
        if self.sender_exceptions is None:
            sender_exception_file = self.config.get(self.section, 'sender_exceptions_file')
            if sender_exception_file:
                self.sender_exceptions = FileList(sender_exception_file, additional_filters=email_normalise_ebl)

        if self.alert_exceptions is None:
            alert_exception_file = self.config.get(self.section, 'alert_exceptions_file')
            if alert_exception_file:
                self.alert_exceptions = FileList(alert_exception_file, additional_filters=email_normalise_ebl)

    async def examine(self, suspect):
        if not REDIS_ENABLED:
            return DUNNO

        if suspect.from_address == '' or suspect.from_address is None:
            return DUNNO

        self._init_lists()
        if self.sender_exceptions and email_normalise_ebl(suspect.from_address) in set(self.sender_exceptions.get_list()):
            return DUNNO

        digest, count = suspect.get_tag('FuZor', (None, 0))

        if digest is None:
            self.logger.debug(f'{suspect.id} digest is none... -> calculate')
            maxsize = self.config.getint(self.section, 'maxsize')
            if suspect.size > maxsize:
                stripoversize = self.config.getboolean(self.section, 'stripoversize')
                if stripoversize:
                    self.logger.debug(f'{suspect.id} Fuzor: message too big {suspect.size}, stripping down to {maxsize}')
                    msgrep = message_from_bytes(
                        suspect.source_stripped_attachments(maxsize=maxsize), _class=PatchedMessage
                    )
                else:
                    self.logger.debug('%s Fuzor: message too big (%u > %u), skipping' % (suspect.id, suspect.size, maxsize))
                    return DUNNO
            else:
                msgrep = suspect.get_message_rep()
            
            hash_algo = self.config.get(self.section, 'hash_algo')
            digest = FuzorDigest(msgrep, hash_algo).digest
            if digest is None and self.config.getboolean(self.section, 'rate_limit_none_digest'):
                digest = '00000000000000000000000000000000'
            self.logger.debug(f'{suspect.id} digest is {digest if digest else "<none>"}')

            if digest is not None:
                try:
                    self._init_backend()
                except RETRY_ON_EXCS as e:
                    self.logger.error(f'{suspect.id} failed to connect to redis server: {e.__class__.__name__}: {str(e)}')
                    return DUNNO

                if self.backend is None:
                    self.logger.warning(f'{suspect.id} failed to initialise fuzor backend')
                    return DUNNO

                attempts = 2
                while attempts:
                    attempts -= 1
                    try:
                        count = await self.backend.get(digest)
                        self.logger.debug(f'{suspect.id} count is {count}')
                        attempts = 0
                    except RETRY_ON_EXCS as e:
                        msg = f'{suspect.id} failed getting count due to {e.__class__.__name__}: {str(e)}'
                        if attempts:
                            self.logger.warning(msg)
                        else:
                            self.logger.error(msg)
                            return self._problemcode()

        threshold = self.config.getint(self.section, 'threshold')
        if count >= threshold:
            subject = suspect.decode_msg_header(suspect.get_header('subject', ''), logid=suspect.id).lower()
            if suspect.get_header('Auto-Submitted', '').lower().startswith('auto'):
                self.logger.info(f'{suspect.id} skipped auto-submitted')
            elif suspect.get_header('X-Auto-Response-Suppress', '') != '':
                self.logger.info(f'{suspect.id} no autoresponse requested, probably automated mail')
            elif self.subjectkeys and any(key in subject for key in self.subjectkeys):
                self.logger.info(f'{suspect.id} has ignore key(s) {",".join(k for k in self.subjectkeys if k in subject)} in subject')
            else:
                if not self.config.getboolean(self.section, 'demomode'):
                    # ------
                    # send mail if not already sent
                    # apply reject action
                    # ------
                    if not self.alert_exceptions:
                        await self._check_and_send_mail(suspect, digest, count)
                    else:
                        alert_exception_list = set(self.alert_exceptions.get_list())
                        if not email_normalise_ebl(suspect.from_address) in alert_exception_list and not suspect.from_domain in alert_exception_list:
                            await self._check_and_send_mail(suspect, digest, count)

                    actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
                    message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {})
                    self.logger.info(f"{suspect.id} Sending {actioncode_to_string(actioncode)} for sender {suspect.from_address} hash {digest} (seen {count} times)")
                    return actioncode, message
                else:
                    # ---
                    # demo mode - only report
                    # ---
                    self.logger.info(f"{suspect.id} Not blocking mail with hash {digest} (seen {count} times) due to demo mode")

        return DUNNO

    async def _check_and_send_mail(self, suspect, digest, count):
        # check if mail has alredy been sent
        # using a simple counter here because I want to use the same backend (with same ttl) as
        # fuzor reportin (using the FuzorMixin)
        mailsent = 0
        digest_mailsent = None
        if digest:
            digest_mailsent = digest + "_mailsent"
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    self._init_backend()
                    mailsent = await self.backend.get(digest_mailsent)
                    attempts = 0
                except RETRY_ON_EXCS as e:
                    msg = f'{suspect.id} failed getting mail sent count due to {str(e)}'
                    self.logger.warning(msg) if attempts else self.logger.error(msg)

        if mailsent == 0 and digest_mailsent is not None:
            self._send_mail(suspect, digest, count)
            # store in Redis mail has been sent...
            try:
                self._init_backend()
                mailsent = await self.backend.increase(digest_mailsent)
                self.logger.info(f'{suspect.id} mail with hash {digest} has been sent {mailsent}')
            except RETRY_ON_EXCS as e:
                self.logger.error(f'{suspect.id} failed increasing mail sent count due to {str(e)}')

    def _send_mail(self, suspect, digest, count):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info(f'{suspect.id} not reported because report recipient is not defined')
            return

        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''

        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        login = get_login_from_suspect(suspect, sasl_hdr)
        tmpldata = {'sasl_login': login}
        account_uri = apply_template(self.config.get(self.section, 'account_uri_template'), suspect, tmpldata)
        search_uri = apply_template(self.config.get(self.section, 'search_uri_template'), suspect, tmpldata)
        
        subject = suspect.decode_msg_header(suspect.get_header('subject', ''), logid=suspect.id)
        
        body = f'Sender: {suspect.from_address}\n'
        body += f'Recipient: {" ".join(suspect.recipients)}\n'
        body += f'Suspect ID: {suspect.id}\n'
        body += f'Fuzor hash: {digest}\n'
        body += f'Fuzor count:{count}s\n'
        body += f'Subject: {subject}\n'
        if account_uri:
            body += f'Account: {account_uri}\n'
        if search_uri:
            body += f'Search: {search_uri}'

        subject = apply_template(self.config.get(self.section, 'subject_template'), suspect, tmpldata)
        msg = suspect.wrap(reporter, reportto, subject, body, 'bulk.eml', self.config)

        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info(
            f'{suspect.id} Bulk Suspect mail sent to {reportto} with queueid {queueid} for sender {suspect.from_address} and Fuzor hash/count: {digest} / {count}')


class PFQDRateLimit(BMPRCPTMixin, BasicMilterPlugin):
    """
Rate Limiter based on your current postfix queues. Queue estimation is done via PFQD, see https://gitlab.com/fumail/pfqd
    """

    def __init__(self, config, section=None):
        super().__init__(config, section=section)

        self.logger = self._logger()
        self.qstore = None

        self.requiredvars = {
            'maxqueue_domain': {
                'default': '15',
                'description': 'maximum queued mail for any given sender domain before deferring '
                               'further mail from this sender domain'
            },

            'maxqueue_user': {
                'default': '5',
                'description': 'maximum queued mail for any given sender before deferring further mail from this sender'
            },

            'active_queue_factor': {
                'default': '3',
                'description': 'by what multiplicator should active queue be weighted higher than deferred queue'
            },

            'redis_conn': {
                'default': '',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },

            'host_regex': {
                'default': '',
                'description': 'PFQD host filter regex'
            },
        }

    def _init_qstore(self):
        if self.qstore is None:
            class Args(object):
                pass
            args = Args()
            args.ttl = 15
            args.hostname = get_outgoing_helo(self.config)
            args.redisconn = self.config.get(self.section, 'redis_conn')
            self.qstore = QStore(args=args)

    async def _get_queue(self, from_domain, from_address, active_queue_factor):
        host_regex = self.config.get(self.section, 'host_regex')
        if host_regex:
            rgx = re.compile(force_bString(host_regex))
        else:
            rgx = None
        relay_deferred = await self.qstore.get_summary(QStore.QUEUE_DEFERRED, rgx)
        relay_active = await self.qstore.get_summary(QStore.QUEUE_ACTIVE, rgx)
        deferred_size_dom = queue_size(relay_deferred, COL_FROM_DOM, from_domain)
        active_size_dom = queue_size(relay_active, COL_FROM_DOM, from_domain)
        deferred_size_user = queue_size(relay_deferred, COL_FROM_ADDR, from_address)
        active_size_user = queue_size(relay_active, COL_FROM_ADDR, from_address)
        qdom = deferred_size_dom + active_size_dom * active_queue_factor
        quser = deferred_size_user + active_size_user * active_queue_factor
        return qdom, quser

    async def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state:
            # not active in current state
            return True

        fc = FunkyConsole()

        if not self.check_config():
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        if not REDIS_ENABLED:
            print(fc.strcolor("ERROR", "red"), ' redis not available. this plugin will do nothing.')
            return False

        try:
            self._init_qstore()
            reply = await self.qstore.ping()
            if reply:
                print("OK: redis server replied to ping")
            else:
                print("ERROR: redis server did not reply to ping")
                return False

            from_address = 'info@unittest.fuglu.org'
            from_domain = extract_domain(from_address)
            active_queue_factor = self.config.getint(self.section, 'active_queue_factor')
            qdom, quser = await self._get_queue(from_domain, from_address, active_queue_factor)
            print(f'Queue for {from_address}: {qdom}/{quser}')
        except Exception as e:
            self.logger.exception(e)
            print(fc.strcolor("ERROR", "red"), f' {e.__class__.__name__}: {str(e)}')
            return False

        return True

    def _is_welcomelisted(self, sess):
        tagname = 'welcomelisted'
        for key in list(sess.tags[tagname].keys()):
            val = sess.tags[tagname][key]
            if val:
                return True
        return False

    async def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) \
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if not REDIS_ENABLED:
            return sm.CONTINUE

        from_address = sess.from_address
        if from_address:
            from_domain = sess.from_domain
        else:
            self.logger.info(f'{sess.id} no sender address found')
            return sm.CONTINUE

        if self._is_welcomelisted(sess):
            return sm.CONTINUE

        self._init_qstore()
        maxqueue_dom = self.config.getint(self.section, 'maxqueue_domain')
        maxqueue_user = self.config.getint(self.section, 'maxqueue_user')
        active_queue_factor = self.config.getint(self.section, 'active_queue_factor')

        queue_dom = queue_user = 0
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                queue_dom, queue_user = await self._get_queue(from_domain, from_address, active_queue_factor)
                attempts = 0
            except Exception as e:
                queue_dom = queue_user = 0
                msg = f"{sess.id} problem getting queue info: {e.__class__.__name__}: {str(e)}"
                if attempts:
                    self.logger.debug(msg)
                else:
                    self.logger.error(msg)

        if queue_dom > maxqueue_dom * active_queue_factor or queue_user > maxqueue_user * active_queue_factor:
            self.logger.info(f'{sess.id} current queue for {from_domain} is {queue_dom} and {from_address} is {queue_user}')
            return sm.TEMPFAIL, 'sender queue limit exceeded - try again later'

        return sm.CONTINUE



class ToCCLimit(ScannerPlugin):
    """
    Limit number of recipients in To and CC header
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'max_to': {
                'default': '0',
                'description': 'maximum number of recipients in To: header. set to 0 for no limit.',
            },
            'max_cc': {
                'default': '0',
                'description': 'maximum number of recipients in CC: header. set to 0 for no limit.',
            },
            'max_rcpt': {
                'default': '0',
                'description': 'maximum number of recipients in To: and CC: headers combined. set to 0 for no limit.',
            },
            'rejectmessage': {
                'default': 'maximum number of recipients in header ${header} exceeded (${count}>${max_hdr})',
                'description': 'reject message template for policy violators'
            },
        }

    def examine(self, suspect):
        hdrs = {'to':0, 'cc':0}
        
        for hdr in hdrs:
            value = suspect.parse_from_type_header(hdr)
            option = f'max_{hdr}'
            max_hdr = suspect.get_tag('filtersettings', {}).get(option, self.config.getint(self.section, option))
            count = len(value)
            hdrs[hdr] = count
            if 0 < max_hdr < count:
                valdict = {'header': hdr, 'count': count, 'max_hdr': max_hdr}
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, valdict)
                return REJECT, message
        
        total_rcpt = sum(hdrs.values())
        max_rcpt = suspect.get_tag('filtersettings', {}).get('max_rcpt', self.config.getint(self.section, 'max_rcpt'))
        if 0 < max_rcpt < total_rcpt:
            valdict = {'header': ','.join(list(hdrs.keys())), 'count': total_rcpt, 'max_hdr': max_rcpt}
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, valdict)
            return REJECT, message
        
        countstr = ' '.join([f'{k}={v}' for k,v in hdrs.items()])
        self.logger.debug(f'{suspect.id} header rcpt total={total_rcpt} {countstr}')
        
        return DUNNO, None
    
    
    def lint(self):
        values = []
        for option in ['max_to', 'max_cc', 'max_rcpt']:
            value = self.config.getint(self.section, option)
            if value < 0:
                print(f'ERROR: negative value {values} for option {option}')
                return False
            values.append(value)
        if not any(values):
            print(f'INFO: all config values are set to 0, this plugin will do nothing')
        return True



class FromNameCounter(ExpiringCounter):
    
    async def _add(self, key:str, value:str) -> tp.Optional[tp.Dict[str,str]]:
        try:
            ts = int(time.time()) + self.ttl
            rds = await self.aioredisbackend.get_redis()
            pipe = await rds.pipeline()
            pipe.hset(key, value, str(ts))  # returns the number of updates (0 or 1 in this case)
            pipe.expire(key, self.ttl)  # returns None
            pipe.hgetall(key) # returns the updated data dict
            async with asyncio.timeout(self.timeout):
                result = await pipe.execute()
            return result[2]
        except RETRY_ON_EXCS:
            return None
    
    async def check_update_name(self, key:str, value:str, cleanup: bool = True, readonly: bool = False) -> int:
        """
        check how many usernames have been seen for an address.
        :param key: the email address to be tested
        :param value: the username to be tested
        :param cleanup: expire old values
        :param readonly: only read, do not add new values or expire old ones
        :return: count how often username was seen for address
        """
        count = 0
        delkeys = []
        values = await self.aioredisbackend.hgetall(force_bString(key), timeout=self.timeout)
        
        do_add = True
        if self.maxcount > 0:
            if len(values) > self.maxcount:
                do_add = False
        
        if do_add and not readonly:
            newval = await self._add(key, value)
            if newval is not None:
                values = newval
        elif not readonly:
            await self.aioredisbackend.expire(force_bString(key), self.ttl, timeout=self.timeout)
        
        ts = int(time.time())
        for k, v in values.items():
            if self._to_int(v) > ts:  # only count current keys
                count += 1
            elif cleanup:  # mark stale keys for cleanup
                delkeys.append(force_bString(k))
                
        if delkeys and len(delkeys) == len(values):
            # all keys are stale
            await self.aioredisbackend.delete(force_bString(key), timeout=self.timeout)
        elif delkeys:
            await self.aioredisbackend.hdel(force_bString(key), mapping=delkeys, timeout=self.timeout)
        return count


class FromNameCheck(AIORedisMixin, BMPHeaderMixin, BasicMilterPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.requiredvars = {
            'state': {
                'default': sm.HEADER,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'redis_ttl': {
                'default': str(12 * 3600),
                'description': 'TTL in seconds',
            },
            
            'redis_timeout': {
                'default': '2',
                'description': 'redis timeout in seconds'
            },
            
            'threshold': {
                'default': '10',
                'description': 'number of different from names accepted during redis_ttl timespan'
            },
            
            'max_count': {
                'default': '1000',
                'description': 'do not increase counter beyond this value (for performance reasons)'
            },

            'actioncode': {
                'default': 'reject',
                'description': "plugin action if policy is violated (continue, reject, tempfail)",
            },
            
            'rejectmessage': {
                'default': 'too many from header name changes - check if your mailbox got abused',
                'description': 'reject message template for policy violators'
            },
            
            'problemaction': {
                'default': 'continue',
                'description': "action if there is a problem (continue, tempfail)",
            },

            'sender_exceptions_file': {
                'default': '${confdir}/fromname_exceptions.txt',
                'description': 'file with permitted senders (no block, no reject)'
            },
        }
        self.sender_exceptions = None
        self.backend_redis = None
    
    def _init_data(self):
        if self.sender_exceptions is None:
            sender_exception_file = self.config.get(self.section, 'sender_exceptions_file')
            if sender_exception_file:
                self.sender_exceptions = FileList(sender_exception_file, additional_filters=email_normalise_ebl)
        
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn and REDIS_ENABLED:
            ttl = self.config.getint(self.section, 'redis_ttl')
            maxcount = self.config.getint(self.section, 'max_count')
            timeout = self.config.getint(self.section, 'redis_timeout', fallback=3)
            self.backend_redis = FromNameCounter(self.aioredisbackend, ttl, maxcount=maxcount, timeout=timeout)
    
    
    def _hdr_extract(self, value:bytes) -> tp.Tuple[tp.Optional[str], tp.Optional[str]]:
        hdrname = hdrfrom = None
        hdrdata = [force_uString(value)]
        try:
            hdrdata = email.utils.getaddresses(hdrdata, strict=False) # new in 3.11.10 and 3.12.5
        except TypeError:
            hdrdata = email.utils.getaddresses(hdrdata)
        if hdrdata and hdrdata[0] and hdrdata[0]:
            hdrname, hdrfrom = hdrdata[0]
            hdrfrom = email_normalise_ebl(hdrfrom)
        return hdrname, hdrfrom
    
    
    async def examine_header(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], key: bytes, value: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if not REDIS_ENABLED:
            return sm.CONTINUE
        
        self._init_data()
        if self.backend_redis is None:
            self.logger.error(f'{sess.id} plugin enabled but not redis config set')
            return sm.CONTINUE
        
        if key.lower() == b'from':
            sender = email_normalise_ebl(force_uString(sess.sender)) if sess.sender else None
            hdrname, hdrfrom = self._hdr_extract(value)
            if hdrname and hdrfrom:
                self.logger.debug(f'{sess.id} env={sender} hdr={hdrfrom} name={hdrname}')
                
                if self.sender_exceptions is not None:
                    exceptions = set(self.sender_exceptions.get_list())
                    if hdrfrom in exceptions or (sender and email_normalise_ebl(sender) in exceptions):
                        self.logger.debug(f'{sess.id} header sender {hdrfrom} or envelope from {sender} is on exception list')
                        return sm.CONTINUE
                
                for addr in [hdrfrom, sender]:
                    if not addr:
                        continue
                    count = await self.backend_redis.check_update_name(addr, hdrname)
                    if count > self.config.getint(self.section, 'threshold'):
                        self.logger.info(f'{sess.id} too many from names {count} by {hdrfrom} via {sender}')
                        suspect = Suspect(sender, force_uString(sess.recipients[0]), None, id=sess.id,
                                          queue_id=sess.queueid, milter_macros=sess.milter_macros, inbuffer=b'\r\n')
                        message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {})
                        action = sm.STR2RETCODE.get(self.config.get(self.section, 'actioncode').lower())
                        return action, message
            else:
                self.logger.debug(f'{sess.id} failed to extract name or address from {force_uString(value)}')
        return sm.CONTINUE

    async def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True
        
        if not self.check_config():
            return False
        
        self._init_data()
        sender_exception_file = self.config.get(self.section, 'sender_exceptions_file')
        if sender_exception_file and not self.sender_exceptions:
            print(f'ERROR: could not load {sender_exception_file}')
            return False
        
        redis_conn = self.config.get(self.section, 'redis_conn')
        if not REDIS_ENABLED:
            print('WARNING: redis unavailable - this plugin will do nothing')
        elif not redis_conn:
            print('WARNING: redis config not set - this plugin will do nothing')
        elif self.backend_redis is None:
            print(f'ERROR: failed to initialize redis backend')
            return False
        else:
            reply = await self.aioredisbackend.ping()
            if not reply:
                print(f'ERROR cannot ping redis server {redis_conn}')
                return False
        
        return True


class EnforceFromSender(BMPEOHMixin, BasicMilterPlugin):
    """
    Enforce RFC validity of From and Sender headers:
    if multiple addresses are present in from header, then a sender header with exactly one address must be present
    """
    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.requiredvars = {
            'state': {
                'default': sm.EOH,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'rejectmessage': {
                'default': 'cannot determine actual sender via from/sender headers',
                'description': f'reject message on policy violation'
            },
            
            'testmode': {
                'default': 'False',
                'description': f'do not reject, log only'
            },
        }
    
    
    def examine_eoh(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        from_addrs = []
        sender_addrs = []
        for key, value in sess.original_headers:
            if key.lower() == b'from':
                for display, address in email.utils.getaddresses([force_uString(value)]):
                    from_addrs.append(address)
            elif key.lower() == b'sender':
                for display, address in email.utils.getaddresses([force_uString(value)]):
                    sender_addrs.append(address)
        
        if len(from_addrs)==1:
            self.logger.debug(f'{sess.id} got exactly one from header address')
            return sm.CONTINUE
        if len(from_addrs)==0:
            self.logger.debug(f'{sess.id} got no from header address')
            return sm.CONTINUE
        elif len(from_addrs) > 1 and len(sender_addrs)==1:
            self.logger.debug(f'{sess.id} got multiple from header addresses but exactly one sender header address')
            return sm.CONTINUE
        elif len(from_addrs) > 1 and len(sender_addrs)==0:
            self.logger.debug(f'{sess.id} got multiple from header addresses but no sender header address')
            if self.config.getboolean(self.section, 'testmode'):
                return sm.CONTINUE
            else:
                rejectmessage = self.config.get(self.section, 'rejectmessage')
                return sm.REJECT, rejectmessage
        elif len(from_addrs) > 1 and len(sender_addrs)>1:
            self.logger.debug(f'{sess.id} got multiple from header addresses and multiple sender header addresses')
            if self.config.getboolean(self.section, 'testmode'):
                return sm.CONTINUE
            else:
                rejectmessage = self.config.get(self.section, 'rejectmessage')
                return sm.REJECT, rejectmessage
        else:
            self.logger.warning(f'{sess.id} got unpredicted from/sender header address combo: from={from_addrs} sender={sender_addrs}')
            return sm.CONTINUE


class NoInvalidFrom(BMPHeaderMixin, BasicMilterPlugin):
    """
    Enforce RFC validity of From headers:
    if sender ends in @domain.invalid (usually set by receiving postfix if header was misformatted), then reject mail.
    """
    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.requiredvars = {
            'state': {
                'default': sm.HEADER,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'rejectmessage': {
                'default': 'cannot determine actual sender via from/sender headers',
                'description': f'reject message on policy violation'
            },
            
            'testmode': {
                'default': 'False',
                'description': f'do not reject, log only'
            },
        }
    
    def examine_header(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], key: bytes, value: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if key.lower() == b'from':
            noaddr = True
            for display, address in email.utils.getaddresses([force_uString(value)]):
                if address and '@' in address:
                    noaddr = False
                if address.endswith == '@domain.invalid':
                    self.logger.debug(f'{sess.id} invalid address {address} in from header {force_uString(value)}')
                    if not self.config.getboolean(self.section, 'testmode'):
                        rejectmessage = self.config.get(self.section, 'rejectmessage')
                        return sm.REJECT, rejectmessage
            if noaddr:
                self.logger.warning(f'{sess.id} no valid address in from header {force_uString(value)}')
        return sm.CONTINUE

    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True
        
        return self.check_config()
    
    
class RCPTDomainThrottle(BMPRCPTMixin, BasicMilterPlugin):
    """
    limit max number of rcpts in a single mail domain group
    """

    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.nobounce = None
        self.nobounce_mx = None

        self.requiredvars = {
            'rcptrgx': {
                'default': '',
                'description': r'regex applied to domain. must contain a group "domain", e.g. r"^(?P<domain>gmx)\."'
            },
            'domainlimits': {
                'default': 'gmx:25',
                'description': 'max number of recipients per domain group as a comma separated list of domaingroup:count, e.g. gmx:25, gmail:50'
            },
            'rejectmessage': {
                'default': 'too many recipients to ${to_domain}',
                'description': 'defer message template for policy violators'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
        self.rgxcache = {}
        self.domainlimits = None
    
    def lint(self, state=None):
        ok = self.check_config()
        if ok :
            rcptrgx = self.config.get(self.section, 'rcptrgx')
            if not rcptrgx:
                print('WARNING: rcptrgx is empty')
            else:
                try:
                    re.compile(rcptrgx, re.I)
                except Exception as e:
                    print(f'ERROR: failed to compile rcptrgx {rcptrgx} due to {e.__class__.__name__}: {str(e)}')
                    ok = False
        if ok:
            self._init_domainlimits()
            print(f'INFO: domainlimits: {self.domainlimits}')
        return ok
    
    def _init_domainlimits(self):
        if self.domainlimits is None:
            dl = self.config.getlist(self.section, 'domainlimits')
            domainlimits = {}
            for item in dl:
                if ':' in item:
                    k,v = item.rsplit(':',1)
                    try:
                        v = int(v)
                    except (TypeError, ValueError):
                        v = 0
                    domainlimits[k] = v
            if domainlimits:
                self.domainlimits = domainlimits
    
    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) \
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        
        rcptrgx = self.config.get(self.section, 'rcptrgx')
        if not rcptrgx:
            return sm.CONTINUE
        
        rgx = self.rgxcache.get(rcptrgx)
        if rgx is None:
            rgx = re.compile(rcptrgx, re.I)
            self.rgxcache[rcptrgx] = rgx
        
        to_domain = email_normalise_ebl(force_uString(recipient)).rsplit('@',1)[-1]
        match = rgx.match(to_domain)
        if match:
            rcptgroup = match.groupdict().get('domain')
            if rcptgroup:
                if 'rcptgroup' in sess.tags:
                    try:
                        sess.tags['rcptgroup'][rcptgroup] += 1
                    except KeyError:
                        sess.tags['rcptgroup'][rcptgroup] = 1
                else:
                    sess.tags['rcptgroup'] = {rcptgroup: 1}
                
                self._init_domainlimits()
                limit = self.domainlimits.get(rcptgroup)
                if limit is not None:
                    if sess.tags['rcptgroup'][rcptgroup] > limit:
                        rejstring = self.config.get(self.section, 'rejectmessage')
                        tmpl = Template(rejstring)
                        fields = sess.get_templ_dict()
                        fields['to_domain'] = to_domain
                        rejectmessage = tmpl.safe_substitute(fields)
                        return sm.TEMPFAIL, rejectmessage
        return sm.CONTINUE
        
        
        