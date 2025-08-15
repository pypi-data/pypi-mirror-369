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

__version__ = "0.0.5"

import os
import re
import ipaddress
import typing as tp

from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.stringencode import force_uString
from fuglu.shared import _SuspectTemplate, FileList


class OriginPolicyCache(FileList):
    def __init__(self, filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=False,
                 additional_filters=None, minimum_time_between_reloads=5):
        self.addresses = {}
        self.names = {}
        super().__init__(filename, strip, skip_empty, skip_comments, lowercase, additional_filters, minimum_time_between_reloads)

    def _reload(self, retry=1):
        regex_ip = '^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?|[a-f0-9:]{3,39})$'
        try:
            with open(self.filename) as fp:
                lines = fp.readlines()
        except Exception as e:
            self.logger.error(f"Skip because of error in reload for file {force_uString(self.filename)} OriginPolicyCache: {str(e)}")
            return

        for line in lines:
            line.strip()
            if line and not line.startswith('#'):
                data = line.split(None, 1)

                if len(data) != 2:
                    continue

                domain = data[0]
                nets = data[1]

                for item in nets.split(','):
                    item = item.strip().lower()
                    if not item:
                        continue
                    if re.match(regex_ip, item):
                        if not domain in self.addresses:
                            self.addresses[domain] = []

                        item = ipaddress.ip_network(item, False)
                        if not item in self.addresses[domain]:
                            self.addresses[domain].append(item)
                    else:
                        if not domain in self.names:
                            self.names[domain] = []
                        if not item in self.names[domain]:
                            self.names[domain].append(item)

    def _permitted_ip(self, domain, ip):
        if domain not in self.addresses:
            return True

        perm = False
        for net in self.addresses[domain]:
            if ipaddress.ip_address(ip) in net:
                perm = True
                break
        return perm

    def _permitted_name(self, domain, hostname):
        if domain not in self.names:
            return True

        perm = False
        for name in self.names[domain]:
            if hostname == name or hostname.endswith('.%s' % name):
                perm = True
                break
        return perm

    def permitted(self, domain, ip, hostname, default=True):
        self._reload_if_necessary()

        # domain is not listed, we accept mail from everywhere
        if not domain in self.addresses and not domain in self.names:
            return default

        ip_perm = self._permitted_ip(domain, ip)
        name_perm = self._permitted_name(domain, hostname)

        return ip_perm and name_perm


class OriginPolicy(BMPRCPTMixin, BasicMilterPlugin):
    """
    This plugin allows to configure from which hosts you
    are willing to accept mail for a given domain.

    Check by recipient domain (MX Rules):
    This can be useful if you provide shared hosting (= many domains on one mail 
    server) and some of the domains use a cloud based spam filter (= MX records 
    not pointing directly to your hosting server). You can reject mail coming 
    from unexpected hosts trying to bypass the spam filter. 

    Check by sender domain (SPF Rules):
    Some domains/freemailers do not have an SPF record, although their 
    domains are frequently forged and abused as spam sender. 
    This plugin allows you to build your own fake SPF database.

    Check forward block (FWD Rules):
    Some users forward abusive amounts of unproperly filtered mail. This mail is hard
    to filter as it's delivered through an additional relay, leading to unnecessary high
    amounts of false negatives. To protect recipients and spam filter reputation such
    mail can be blocked.
    """

    def __init__(self,  config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.mxrules = None
        self.spfrules = None
        self.fwdrules = None

        self.requiredvars = {
            'datafile_mx': {
                'default': '${confdir}/conf.d/enforcemx.txt',
                'description': 'recipient domain based rule file',
            },
            'messagetemplate_mx': {
                'default': 'We do not accept mail for ${to_address} from ${reverse_client_address}. Please send to MX records!',
                'description': 'reject message template for mx policy violators'
            },

            'datafile_spf': {
                'default': '${confdir}/conf.d/fakespf.txt',
                'description': 'sender domain based rule file',
            },
            'messagetemplate_spf': {
                'default': 'We do not accept mail for ${from_domain} from ${client_address} with name ${reverse_client_name}. Please use the official mail servers!',
                'description': 'reject message template for fake spf policy violators'
            },

            'datafile_fwd': {
                'default': '${confdir}/conf.d/forwardblock.txt',
                'description': 'sender domain based rule file',
            },
            'messagetemplate_fwd': {
                'default': 'We do not accept forwarded mail for ${to_address} from ${reverse_client_name}.',
                'description': 'reject message template for forward policy violators'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        client_address = force_uString(sess.addr)
        if client_address is None:
            self.logger.error(f'{sess.id} No client address found - skipping')
            return sm.CONTINUE

        client_name = force_uString(sess.fcrdns)
        if client_name is None:
            client_name = 'unknown'

        to_address = force_uString(recipient)
        if to_address:
            to_address = to_address.lower()

        action, message = self._examine_mx(sess, client_address, client_name, to_address)
        if action == sm.CONTINUE:
            action, message = self._examine_spf(sess, client_address, client_name)
        if action == sm.CONTINUE:
            action, message = self._examine_fwd(sess, client_address, client_name, to_address)

        if message:
            return action, message
        else:
            return action

    def _examine_mx(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], client_address: str, client_name: str, to_address: str) -> tp.Tuple[bytes, tp.Optional[str]]:
        if not to_address:
            self.logger.warning(f'{sess.id} No RCPT address found')
            return sm.TEMPFAIL, 'internal policy error (no rcpt address)'

        to_domain = sm.MilterSession.extract_domain(to_address)

        if not self.mxrules:
            datafile = self.config.get(self.section, 'datafile_mx')
            if os.path.exists(datafile):
                self.mxrules = OriginPolicyCache(datafile)
                self.logger.debug(f"{sess.id} examine_mx datafile \"{datafile}\" found, RulesCache set up")
            else:
                self.logger.debug(f"{sess.id} examine_mx datafile \"{datafile}\" not found, skip...")
                return sm.CONTINUE, None

        action = sm.CONTINUE
        message = None
        if not self.mxrules.permitted(to_domain, client_address, client_name):
            if client_name == 'unknown':
                action = sm.TEMPFAIL
            else:
                action = sm.REJECT
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate_mx'))
            templ_dict = sess.get_templ_dict()
            message = template.safe_substitute(templ_dict)

        return action, message

    def _examine_spf(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], client_address: str, client_name: str) -> tp.Tuple[bytes, tp.Optional[str]]:
        from_address = force_uString(sess.sender)

        if from_address is None:
            self.logger.warning(f'{sess.id} No FROM address found')
            return sm.TEMPFAIL, 'internal policy error (no from address)'

        from_domain = sm.MilterSession.extract_domain(from_address)

        if not self.spfrules:
            datafile = self.config.get(self.section, 'datafile_spf')
            if os.path.exists(datafile):
                self.spfrules = OriginPolicyCache(datafile)
                self.logger.debug(f"{sess.id} examine_spf datafile \"{datafile}\" found, RulesCache set up")
            else:
                self.logger.debug(f"{sess.id} examine_spf datafile \"{datafile}\" not found, skip...")
                return sm.CONTINUE, None

        action = sm.CONTINUE
        message = None
        if not self.spfrules.permitted(from_domain, client_address, client_name):
            if client_name == 'unknown':
                action = sm.TEMPFAIL
            else:
                action = sm.REJECT
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate_spf'))
            templ_dict = sess.get_templ_dict()
            message = template.safe_substitute(templ_dict)

        return action, message

    def _examine_fwd(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], client_address: str, client_name: str, to_address: str) -> tp.Tuple[bytes, tp.Optional[str]]:

        if not to_address:
            self.logger.warning(f'{sess.id} No RCPT address found')
            return sm.TEMPFAIL, 'internal policy error (no rcpt address)'

        to_domain = sm.MilterSession.extract_domain(to_address)

        if not self.fwdrules:
            datafile = self.config.get(self.section, 'datafile_fwd')
            if os.path.exists(datafile):
                self.fwdrules = OriginPolicyCache(datafile)
                self.logger.debug(f"{sess.id} examine_fwd datafile \"{datafile}\" found, RulesCache set up")
            else:
                self.logger.debug(f"{sess.id} examine_fwd datafile \"{datafile}\" not found, skip...")
                return sm.CONTINUE, None

        action = sm.CONTINUE
        message = None
        self.logger.debug(f"{sess.id} fwdrules check permitted to={to_domain}, ca={client_address}, cn={client_name}")
        if self.fwdrules.permitted(to_domain, client_address, client_name, default=False) \
                or self.fwdrules.permitted(to_address, client_address, client_name, default=False):
            if not sess.ptr or sess.ptr == 'unknown':
                action = sm.TEMPFAIL
            else:
                action = sm.REJECT
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate_fwd'))
            templ_dict = sess.get_templ_dict()
            templ_dict['to_domain'] = to_domain
            templ_dict['client_address'] = client_address
            templ_dict['client_name'] = client_name
            message = template.safe_substitute(templ_dict)

        return action, message

    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        lint_ok = True

        if not self.check_config():
            print('Error checking config')
            lint_ok = False

        check_mx = True
        datafile = self.config.get(self.section, 'datafile_mx')
        if datafile and not os.path.exists(datafile):
            print('MX datafile not found - this plugin will not enforce MX usage')
            check_mx = False

        check_spf = True
        datafile = self.config.get(self.section, 'datafile_spf')
        if datafile and not os.path.exists(datafile):
            print('SPF datafile not found - this plugin will not check fake SPF')
            check_spf = False

        check_fwd = True
        datafile = self.config.get(self.section, 'datafile_fwd')
        if datafile and not os.path.exists(datafile):
            print('Forward block datafile not found - this plugin will not check forwards')
            check_fwd = False

        if not (check_mx or check_spf or check_fwd):
            lint_ok = False

        return lint_ok

    def __str__(self):
        return self.__class__.__name__
