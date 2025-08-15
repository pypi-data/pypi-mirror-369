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

import typing as tp
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, get_domain_setting, text
from fuglu.mshared import BMPEOBMixin, BasicMilterPlugin
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.stringencode import force_uString
from fuglu.shared import _SuspectTemplate, get_default_cache


class MessageSize(BMPEOBMixin, BasicMilterPlugin):

    """
    This plugin allows setting individual message size limits per recipient domain
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'datasource': {
                'default': '',
                'description': """
                    sql:SELECT max_size from domain where domain_name=:domain - get from sql database :domain will be replaced with the actual domain name. must return one integer field containing maximum size in bytes
                    tag:filtersettings:max_message_size - get from p_blwl FilterSettings backend tag. use ${domain} and ${recipient} in tag name for specific per domain/recipient overrides
                    """,
            },
            'dbconnection': {
                'default': "mysql://root@localhost/config?charset=utf8",
                'description': 'SQLAlchemy Connection string. Leave empty to disable SQL lookups',
            },
            'messagetemplate': {
                'default': 'message size ${msg_size} exceeds size limit ${max_size} of recipient domain ${to_domain}',
                'description': 'reject message template for policy violators'
            },
            'state': {
                'default': asm.EOB,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def _get_domain_limit(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], to_domain: str, recipient: str) -> tp.Union[int, None]:
        max_size = None
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        datasource = self.config.get(self.section, 'datasource')

        if SQL_EXTENSION_ENABLED and datasource.startswith('sql:') and dbconnection != '':
            cache = get_default_cache()
            sqlquery = datasource[4:]
            # use DBConfig instead of get_domain_setting
            max_size = get_domain_setting(to_domain, dbconnection, sqlquery, cache, self.section, False, self.logger)

        elif datasource.startswith('tag:'):
            keylist = datasource.split(':')[1:]
            value = sess.tags.copy()
            for key in keylist:
                if key.startswith('$'):
                    template = _SuspectTemplate(key)
                    key = template.safe_substitute({'recipient': recipient, 'domain': to_domain})
                value = value.get(key, {})
                if isinstance(value, (int, float)):
                    max_size = int(value)
                    break

        return max_size

    def examine_eob(self, sess: tp.Union[sm.MilterSession, asm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        datasource = self.config.get(self.section, 'datasource')
        if not SQL_EXTENSION_ENABLED and datasource.startswith('sql:'):
            return sm.CONTINUE

        recipients = [force_uString(r) for r in sess.recipients if r]

        if not recipients:
            self.logger.error(f'{sess.id} No TO address found')
            return sm.CONTINUE

        try:
            msg_size = sess.size
        except (ValueError, TypeError):
            msg_size = 0

        if msg_size <= 0:
            self.logger.debug(f'{sess.id} skipped: message size unknown (not specified or not in end-of-data restrictions)')
            return sm.CONTINUE

        max_size_reduced = None
        
        for recipient in recipients:
            to_domain = recipient.rsplit('@',1)[-1]
            max_size = self._get_domain_limit(sess, to_domain, recipient)
            if max_size:
                if max_size_reduced is None:
                    max_size_reduced = max_size
                else:
                    #max_size_reduced = min(max_size, max_size_reduced)
                    # use maximum to see if someone can receive...
                    max_size_reduced = max(max_size, max_size_reduced)

        if max_size_reduced is None or max_size_reduced <= 0:
            self.logger.debug(f'{sess.id} skipped: no max size for recipient{"s" if len(recipients) > 1 else ""} {", ".join(recipients)} specified')
            return sm.CONTINUE
        self.logger.debug(f'{sess.id} max size for recipient{"s" if len(recipients) > 1 else ""} {", ".join(recipients)} is {max_size_reduced} message size is {msg_size}')

        if msg_size > max_size_reduced:
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
            templ_dict = sess.get_templ_dict()
            templ_dict['msg_size'] = msg_size
            templ_dict['max_size'] = max_size_reduced
            message = template.safe_substitute(templ_dict)
            return sm.REJECT, message

        return sm.CONTINUE

    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True
        
        datasource = self.config.get(self.section, 'datasource')
        if not SQL_EXTENSION_ENABLED and datasource.startswith('sql:'):
            print("sqlalchemy is not installed")
            return False

        if not self.check_config():
            return False

        try:
            dbconnection = self.config.get(self.section, 'dbconnection')
            if dbconnection:
                conn = get_session(dbconnection)
                conn.execute(text("SELECT 1"))
        except Exception as e:
            print("Failed to connect to SQL database: %s" % str(e))
            return False

        return True


class LineLength(BMPEOBMixin, BasicMilterPlugin):

    """
    This plugin checks for excessively long lines in the mail content
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'maxlength': {
                'default': str(1024*25),
                'description': 'maximum number of characters per line',
            },
            'messagetemplate': {
                'default': 'message contains excessively long lines',
                'description': 'reject message template for policy violators'
            },
            'state': {
                'default': asm.EOB,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
        
    def examine_eob(self, sess: tp.Union[sm.MilterSession, asm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        maxsize = self.config.getint(self.section, 'maxlength')
        exceeded = False
        linesize = 0
        buffer = sess.buffer.getbuffer()
        for line in buffer.tobytes().splitlines():
            linesize = len(line)
            if linesize > maxsize:
                self.logger.warning(f'{sess.id} found excessively long line with length {linesize}')
                exceeded = True
                break
        else:
            self.logger.debug(f'{sess.id} longest line was {linesize} bytes')
        
        if exceeded:
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
            templ_dict = sess.get_templ_dict()
            message = template.safe_substitute(templ_dict)
            return sm.REJECT, message
        
        return sm.CONTINUE
    
    
    def lint(self, state=None) -> bool:
        if not self.check_config():
            return False
        
        try:
            maxsize = self.config.getint(self.section, 'maxlength')
            if maxsize < 1000:
                print(f'WARNING: very small value of maxlength: {maxsize}')
        except Exception as e:
            print(f'ERROR: failed to get maxlength due to {e.__class__.__name__}: {str(e)}')
            return False
        return True
    