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
import os
import typing as tp
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
from fuglu.shared import _SuspectTemplate, FileList, get_default_cache
from fuglu.stringencode import force_uString
from fuglu.extensions.sql import get_domain_setting, SQL_EXTENSION_ENABLED, get_session, text
import fnmatch


class EnforceTLS(BMPRCPTMixin, BasicMilterPlugin):
    """
    set TLS policy by recipient domain. Allows to enforce TLS on per-recipient base
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.selective_domain_loader = None
        self.requiredvars = {
            'datasource': {
                'default': '',
                'description': """
                if this is empty, all recipient domains will be forced to use TLS
                txt:<filename> - get from simple textfile which lists one domain per line
                sql:<statement> - get from sql database :domain will be replaced with the actual domain name. must return one field containing boolean/int value
                tag:filtersettings:enforce_tls - get from p_blwl FilterSettings backend tag
                """,
            },
            'dbconnection': {
                'default': "mysql://root@localhost/enforcetls?charset=utf8",
                'description': 'SQLAlchemy Connection string',
            },
            'action': {
                'default': 'tempfail',
                'description': 'Action if connection is not TLS encrypted. set to continue, tempfail, reject',
            },
            'messagetemplate': {
                'default': 'Unencrypted connection. This recipient requires TLS',
                'description': 'reject message template for policy violators'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def enforce_domain(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: str) -> bool:
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        datasource = self.config.get(self.section, 'datasource')
        enforce = False
        to_domain = sm.MilterSession.extract_domain(recipient)

        if datasource.strip() == '':
            enforce = True

        elif datasource.startswith('txt:'):
            domainfile = datasource[4:]
            if self.selective_domain_loader is None:
                self.selective_domain_loader = FileList(domainfile, lowercase=True)
            for domain in self.selective_domain_loader.get_list():
                if to_domain == domain or domain.startswith('*.') and fnmatch.fnmatch(to_domain, domain):
                    enforce = True
                    break

        # use DBConfig instead of get_domain_setting
        elif SQL_EXTENSION_ENABLED and datasource.startswith('sql:') and dbconnection != '':
            cache = get_default_cache()
            sqlquery = datasource[4:]
            enforce = get_domain_setting(to_domain, dbconnection, sqlquery, cache, self.section, False, self.logger)

        elif datasource.startswith('tag:'):
            keylist = datasource.split(':')[1:]
            value = sess.tags.copy()
            for key in keylist:
                if key.startswith('$'):
                    template = _SuspectTemplate(key)
                    key = template.safe_substitute({'recipient': recipient, 'domain': to_domain})
                value = value.get(key, {})
                if isinstance(value, bool):
                    enforce = value
                    break
            self.logger.debug(f'{sess.id} got {enforce} via {keylist} from {sess.tags}')

        return enforce

    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        """Use asnyc routine because tls info needs async patched milter lib"""
        if not recipient:
            return sm.CONTINUE

        recipient = force_uString(recipient)
        enforce = self.enforce_domain(sess, recipient)
        encryption_protocol = sess.milter_macros.get('tls_version')

        action = sm.CONTINUE
        message = None
        if enforce and not encryption_protocol:
            action = sm.STR2RETCODE.get(self.config.get(self.section, 'action'), action)
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
            templ_dict = sess.get_templ_dict()
            templ_dict['recipient'] = recipient
            message = template.safe_substitute(templ_dict)
        self.logger.info(f"{sess.id} recpient={recipient} enforce={enforce} encproto={force_uString(encryption_protocol)} action={sm.RETCODE2STR.get(action)}")
        return action, message

    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        lint_ok = True
        if not self.check_config():
            print('Error checking config')
            lint_ok = False

        action = sm.STR2RETCODE.get(self.config.get(self.section, 'action'), None)

        if not action:
            lint_ok = False
            print(f"Action value '{self.config.get(self.section, 'action')}' not in allowed "
                  f"choices: 'continue', 'tempfail', 'reject'")

        if lint_ok:
            datasource = self.config.get(self.section, 'datasource')
            if datasource.strip() == '':
                print('Enforcing TLS for all domains')
            elif datasource.startswith('txt:'):
                domainfile = datasource[4:]
                if not os.path.exists(domainfile):
                    print('Cannot find domain file %s' % domainfile)
                    lint_ok = False
            elif datasource.startswith('sql:'):
                sqlquery = datasource[4:]
                if not sqlquery.lower().startswith('select '):
                    lint_ok = False
                    print('SQL statement must be a SELECT query')
                if not SQL_EXTENSION_ENABLED:
                    print('SQLAlchemy not available, cannot use sql backend')
                if lint_ok:
                    dbconnection = self.config.get(self.section, 'dbconnection')
                    try:
                        conn = get_session(dbconnection)
                        conn.execute(text(sqlquery), {'domain': 'example.com'})
                    except Exception as e:
                        lint_ok = False
                        print(str(e))
            elif datasource.startswith('tag:'):
                pass
            else:
                lint_ok = False
                print('Could not determine domain list backend type')

        return lint_ok

    def __str__(self):
        return "EnforceTLS"


class TLSSender(BMPRCPTMixin, BasicMilterPlugin):
    """
    set TLS policy by sender domain. Allows to enforce TLS on per-sender base
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.selective_domain_loader = None
        self.requiredvars = {
            'domains_file': {
                'default': '${confdir}/tls-senders.txt',
                'description': "path to file with sender domains that must use TLS",
            },
            'action': {
                'default': 'reject',
                'description': 'Action if connection is not TLS encrypted. set to continue, tempfail, reject',
            },
            'messagetemplate': {
                'default': 'Unencrypted connection. This sender must use TLS',
                'description': 'reject message template for policy violators'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def enforce_domain(self, from_domain: str) -> bool:
        enforce = False
        domainfile = self.config.get(self.section, 'domains_file')

        if domainfile.strip() == '':
            enforce = True

        if self.selective_domain_loader is None:
            self.selective_domain_loader = FileList(domainfile, lowercase=True)
        for domain in self.selective_domain_loader.get_list():
            if from_domain == domain or domain.startswith('*.') and fnmatch.fnmatch(from_domain, domain):
                enforce = True
                break

        return enforce

    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[
            bytes, tp.Tuple[bytes, str]]:
        """Note this routine is not async atm..."""
        sender = sess.sender

        if not sender:
            return sm.CONTINUE

        sender = force_uString(sender)
        sender_domain = sm.MilterSession.extract_domain(sender)
        enforce = self.enforce_domain(sender_domain)
        encryption_protocol = sess.milter_macros.get('tls_version')

        action = sm.CONTINUE
        message = None
        if enforce and not encryption_protocol:
            action = sm.STR2RETCODE.get(self.config.get(self.section, 'action'), action)
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
            message = template.safe_substitute(sess.get_templ_dict())
        self.logger.info(f"{sess.id} sender={sender} enforce={enforce} encproto={force_uString(encryption_protocol)} action={sm.RETCODE2STR.get(action)}")
        return action, message

    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        lint_ok = True
        if not self.check_config():
            print('Error checking config')
            lint_ok = False

        action = sm.STR2RETCODE.get(self.config.get(self.section, 'action'), None)

        if not action:
            lint_ok = False
            print(f"Action value '{self.config.get(self.section, 'action')}' not in allowed "
                  f"choices: 'continue', 'tempfail', 'reject'")

        if lint_ok:
            domainfile = self.config.get(self.section, 'domains_file')
            if domainfile.strip() == '':
                print('Enforcing TLS for all domains')
            else:
                if not os.path.exists(domainfile):
                    print('Cannot find domain file %s' % domainfile)
                    lint_ok = False

        return lint_ok

    def __str__(self):
        return "TLSSender"
