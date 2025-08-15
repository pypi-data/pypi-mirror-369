# -*- coding: UTF-8 -*-
#   Copyright Oli Schacher, Fumail Project
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
from fuglu.shared import ScannerPlugin, DUNNO, DELETE, string_to_actioncode, SuspectFilter, \
    Suspect, apply_template, REJECT, _SuspectTemplate, actioncode_to_string
from fuglu.extensions.sql import DBConfig
from fuglu.stringencode import force_uString
import os
import re

try:
    from domainmagic.validators import is_email
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False

    def is_email(value):
        return '@' in value


class KillerPlugin(ScannerPlugin):

    """
DELETE all mails (for special mail setups like spam traps etc)
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

    def __str__(self):
        return "delete Message"

    def examine(self, suspect):
        return DELETE

    def lint(self):
        print("""!!! WARNING: You have enabled the KILLER plugin - NO message will forwarded to postfix. !!!""")
        return True


class FilterDecision(ScannerPlugin):
    """
Evaluates possible decision based on results by previous plugins e.g.
 * check results of antivirus scanners
 * check results of spam analyzers
 * archive/quarantine status
 * block/welcomelist or filter settings
 * filtersettings tags, set e.g. by p_blwl FilterSettings backend
and performs the following actions:
 * add headers or subject tags according to filter result
 * decide if mail should be delivered or deleted
 * wrap mail and send as .eml-attachment
 * change the recipient
Because this plugin may change subject (or body when wrapping) it's recommended
to run it before signing plugins such as DKIMSignPlugin or ARCSignPlugin.
This plugin will always return DUNNO, use DeliverDecision as last plugin to issue DELETE if needed.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'wrap_template_file': {
                'default': '',
                'description': 'path to template file used as body for wrapped spam',
            },
            'subject_tag_spam': {
                'default': '[SPAM]',
                'description': 'default tag if message is spam',
            },
            'subject_tag_highspam': {
                'default': '[SPAM]',
                'description': 'default tag if message is highspam',
            },
            'subject_tag_blocked': {
                'default': '[BLOCKED]',
                'description': 'default tag if message is blocked',
            },
            'subject_tag_virus': {
                'default': '[VIRUS]',
                'description': 'default tag if message contains a virus',
            },
            'subject_tag_blocklisted': {
                'default': '[BLOCKLISTED]',
                'description': 'default tag if message is blocklisted',
            },
        }

    def __str__(self):
        return "Filter Decision"

    def lint(self):
        allok = self.check_config()
        if allok:
            wrap_template_file = self.config.get(self.section, 'wrap_template_file')
            if wrap_template_file and not os.path.exists(wrap_template_file):
                print(f'ERROR: wrap_template_file {wrap_template_file} does not exist')
                allok = False
        return allok

    def _get_filtersetting(self, suspect, option, default=None):
        return suspect.get_tag('filtersettings', {}).get(option, default)

    def _subject_updater(self, subject, **params):
        tag = params.get('tag')
        subject = force_uString(subject)
        if tag and subject.startswith(tag): # don't add tag again if subject starts with ext tag
            return subject
        if tag and f'{tag} ' in subject: # remove tag if it is already contained in subject
            subject = subject.replace(f'{tag} ', '')
        if tag:
            subject = f'{tag} {subject}'
        return subject

    def _add_subject_tag_ext(self, suspect):
        subject_tag_level = int(self._get_filtersetting(suspect, 'subject_tag_ext_level', 0))
        self.logger.debug(f'{suspect.id} adding subject ext tags level={subject_tag_level}')
        
        if subject_tag_level == 0:
            # level 0: do not tag
            return
        
        do_tag = False
        if subject_tag_level == 1:
            # level 1: tag every message
            do_tag = True
        elif subject_tag_level >= 2:
            # level 2 and higher: only tag mal from same domain
            to_domain = suspect.to_domain.lower()
            if suspect.from_domain and suspect.from_domain.lower() == to_domain:
                do_tag = True
            else:
                hdr_from_address = suspect.parse_from_type_header(header='From', validate_mail=True)
                if hdr_from_address and hdr_from_address[0]:
                    hdr_from_domain = hdr_from_address[0][1].rsplit('@', 1)[-1]
                    if hdr_from_domain.lower() == to_domain:
                        do_tag = True
            # level 3: do not tag securely welcomelisted mail:
            if do_tag and subject_tag_level == 3 and suspect.is_welcomelisted() and suspect.get_tag('welcomelisted.confirmed'):
                do_tag = False

        subject_tag = self._get_filtersetting(suspect, 'subject_tag_ext')
        if do_tag and subject_tag:
            suspect.update_subject(self._subject_updater, tag=subject_tag)
            self.logger.debug(f'{suspect.id} tagging subject tag={subject_tag}')
        if do_tag:
            prependaddedheaders = self.config.get('main', 'prependaddedheaders')
            suspect.add_header(f'{prependaddedheaders}External', 'yes')
    
    def _add_subject_tag_status(self, suspect, tagname):
        self.logger.debug(f'{suspect.id} adding subject status tag {tagname}')
        subject_tag = self._get_filtersetting(suspect, tagname)
        if not subject_tag:
            subject_tag = self.config.get(self.section, tagname, fallback=None)
        if subject_tag:
            suspect.update_subject(self._subject_updater, tag=subject_tag)
            return True
        return False
    
    def _add_status_markers(self, suspect):
        self.logger.debug(f'{suspect.id} adding status markers')
        prependaddedheaders = self.config.get('main', 'prependaddedheaders')
        if suspect.is_virus():
            suspect.add_header(f'{prependaddedheaders}Virus', 'yes')
            self._add_subject_tag_status(suspect, 'subject_tag_virus')
        elif suspect.is_blocklisted():
            suspect.add_header(f'{prependaddedheaders}Blocklisted', 'yes')
            self._add_subject_tag_status(suspect, 'subject_tag_blocklisted')
        elif suspect.is_blocked():
            suspect.add_header(f'{prependaddedheaders}Blocked', 'yes')
            self._add_subject_tag_status(suspect, 'subject_tag_blocked')
        elif suspect.is_welcomelisted():
            suspect.add_header(f'{prependaddedheaders}Welcomelisted', 'yes')
            self._add_subject_tag_status(suspect, 'subject_tag_welcomelisted')
        elif suspect.is_highspam():
            suspect.add_header(f'{prependaddedheaders}HighSpam', 'yes')
            if not self._add_subject_tag_status(suspect, 'subject_tag_highspam'):
                self._add_subject_tag_status(suspect, 'subject_tag_spam')
        elif suspect.is_spam():
            suspect.add_header(f'{prependaddedheaders}Spam', 'yes')
            self._add_subject_tag_status(suspect, 'subject_tag_spam')
        suspect.set_tag('filterdecision.tagged', True)

    def _check_deliver_spam(self, suspect):
        deliver = True
        if suspect.is_virus():
            deliver = False
        elif suspect.is_blocklisted():
            deliver = False
        elif suspect.is_blocked():
            deliver = False
        elif suspect.is_welcomelisted():
            deliver = True
        elif suspect.is_highspam():
            deliver = False
            if self._get_filtersetting(suspect, 'deliver_highspam', False):
                self.logger.debug(f'{suspect.id} is highspam, but delivering due to filtersetting')
                deliver = True
        elif suspect.is_spam():
            deliver = False
            if self._get_filtersetting(suspect, 'deliver_spam', False):
                self.logger.debug(f'{suspect.id} is spam, but delivering due to filtersetting')
                deliver = True
        
        if deliver and not suspect.is_ham():
            spam_recipient = self._get_filtersetting(suspect, 'spam_recipient')
            if spam_recipient and is_email(spam_recipient):
                self.logger.debug(f'{suspect.id} delivering to spam rcpt {spam_recipient}')
                suspect.to_address = spam_recipient
            elif spam_recipient and not is_email(spam_recipient):
                self.logger.warning(f'{suspect.id} ignoring invalid spam rcpt {spam_recipient}')
        return deliver

    def examine(self, suspect):
        deliver = self._check_deliver_spam(suspect)
        if not deliver:
            suspect.set_tag('filterdecision.action', actioncode_to_string(DELETE))
            self.logger.info(f'{suspect.id} recommend DELETE due to filterdecision')

        orig_subject = suspect.get_header('subject')

        if deliver and not suspect.is_ham():
            self._add_status_markers(suspect)
        self._add_subject_tag_ext(suspect)
        self.logger.debug(f'{suspect.id} tagging completed')

        if deliver and self._get_filtersetting(suspect, 'wrap_spam', False) and suspect.is_spam() \
                or self._get_filtersetting(suspect, 'wrap_highspam', False) and suspect.is_highspam() \
                or self._get_filtersetting(suspect, 'wrap_virus', False) and suspect.is_virus():

            wrap_template_file = self.config.get(self.section, 'wrap_template_file')
            if not wrap_template_file:
                self.logger.error(f'{suspect.id} cannot wrap because wrap_template file not defined')
            elif not os.path.exists(wrap_template_file):
                self.logger.error(f'{suspect.id} cannot wrap because wrap_template file {wrap_template_file} not found')
            else:
                self.logger.debug(f'{suspect.id} wrapping message')
                with open(wrap_template_file) as fp:
                    templatecontent = fp.read()
                body = apply_template(templatecontent, suspect, {})
                msg = suspect.wrap(suspect.from_address, suspect.to_address, orig_subject, body, 'original_mail.eml', self.config)
                suspect.set_source(msg.as_bytes())
                self.logger.debug(f'{suspect.id} wrapped')

        return DUNNO


class DeliverDecision(FilterDecision):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'testmode': {
                'default': 'False',
                'description': 'will not delete any mail if set to True',
            },
        })
    
    def lint(self):
        allok = self.check_config()
        if self.config.get(self.section, 'testmode'):
            print('WARNING: testmode active, will not delete any mail. may forward untagged spam or malware!')
        return allok
    
    def examine(self, suspect):
        action = DUNNO
        decision = suspect.get_tag('filterdecision.action')
        if decision is not None:
            action = string_to_actioncode(decision)
            # message was not archived, we do not want to just discard it
            if action == DELETE and not suspect.is_ham() and not suspect.get_tag('archived', False):
                self.logger.debug(f'{suspect.id} is ham={suspect.is_ham()}, but delivering because archived={suspect.get_tag("archived")}')
                action = DUNNO
                if not suspect.get_tag('filterdecision.tagged'):
                    self._add_status_markers(suspect)
            if action == DELETE and self.config.getboolean(self.section, 'testmode'):
                self.logger.info(f'{suspect.id} testmode enabled. else would be deleting due to filterdecision')
                action = DUNNO
        return action


class StripSubjectTag(FilterDecision):
    """
Removes subject tags that were set by e.g. FilterDecision plugin.
This is useful for outbound mail if FilterDecision tags corresponding inbound mail.
Because this plugin may change subject it's recommended
to run it before signing plugins such as DKIMSignPlugin or ARCSignPlugin.
This plugin will always return DUNNO
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'removetags': {
                'default': 'subject_tag_virus,subject_tag_blocklisted,subject_tag_blocked,subject_tag_welcomelisted,subject_tag_spam,subject_tag_highspam,subject_tag_ext',
                'description': 'comma separated list of tags to remove',
            },
        })
    
    def lint(self):
        allok = self.check_config()
        removetags = self.config.getlist(self.section, 'removetags')
        if removetags:
            print(f'deleting status markers {",".join(removetags)}')
        else:
            print('WARNING: no tags to remove defined')
        return allok
    
    def _subject_updater(self, subject, **params):
        tag = params.get('tag')
        subject = force_uString(subject)
        if tag and f'{tag} ' in subject: # remove tag if it is contained in subject
            subject = subject.replace(f'{tag} ', '')
        return subject
    
    def _del_subject_tag_status(self, suspect, tagname):
        subject_tag_spam = self._get_filtersetting(suspect, tagname)
        if subject_tag_spam:
            self.logger.debug(f'{suspect.id} deleting subject status tag {tagname}')
            suspect.update_subject(self._subject_updater, tag=subject_tag_spam)
            return True
        return False
    
    def examine(self, suspect):
        removetags = self.config.getlist(self.section, 'removetags')
        self.logger.debug(f'{suspect.id} deleting status markers {",".join(removetags)}')
        for tagname in removetags:
            self._del_subject_tag_status(suspect, tagname)
        return DUNNO


class ActionOverridePlugin(ScannerPlugin):

    """
Override actions based on a Suspect Filter file.
For example, delete all messages from a specific sender domain.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'actionrules': {
                'default': '${confdir}/actionrules.regex',
                'description': 'Rules file',
            }
        }
        self.filter = None

    def __str__(self):
        return "Action Override"

    def lint(self):
        allok = self.check_config() and self.lint_filter()

        actionrules = self.config.get(self.section, 'actionrules')
        if actionrules is None or actionrules == "":
            print('WARNING: no actionrules file set, this plugin will do nothing')
        elif not os.path.exists(actionrules):
            print(f'ERROR: actionrules file {actionrules} not found')
            allok = False
        else:
            sfilter = SuspectFilter(actionrules)
            allok = sfilter.lint() and allok

        if not DOMAINMAGIC_AVAILABLE:
            print('WARNING: domainmagic is not installed, REDIRECT targets cannot be validated')
        return allok

    def lint_filter(self):
        filterfile = self.config.get(self.section, 'actionrules')
        sfilter = SuspectFilter(filterfile)
        return sfilter.lint()

    def examine(self, suspect):
        actionrules = self.config.get(self.section, 'actionrules')
        if actionrules is None or actionrules == "" or not os.path.exists(actionrules):
            return DUNNO

        if not os.path.exists(actionrules):
            self.logger.warning(f'{suspect.id} Action Rules file does not exist: {actionrules}')
            return DUNNO

        if self.filter is None:
            self.filter = SuspectFilter(actionrules)

        match, arg = self.filter.matches(suspect)
        if match:
            if arg is None or arg.strip() == '':
                self.logger.warning(f'{suspect.id} Rule match but no action defined')
                return DUNNO

            arg = arg.strip()
            spl = arg.split(None, 1)
            actionstring = spl[0]
            message = None
            if len(spl) == 2:
                message = spl[1]
            self.logger.debug(f'{suspect.id} Rule match! Action override: {arg.upper()}')

            actioncode = string_to_actioncode(actionstring, self.config)
            if actioncode is not None:
                self.logger.info(f'{suspect.id} overriding action to {actionstring}')
                return actioncode, message
            elif actionstring.upper() == 'REDIRECT':
                target = message.strip()
                if is_email(target):
                    orig_to = suspect.to_address
                    suspect.to_address = target
                    self.logger.info(f'{suspect.id} orig_to={orig_to} REDIRECT to={target}')
            else:
                self.logger.error(f'{suspect.id} Invalid action: {arg}')
                return DUNNO

        return DUNNO


class RcptRewrite(ScannerPlugin):
    """
    This plugin reads a new recipient from some header.
    For safety reasons it is recommended to set the header name to a random value and remove the header in postfix after reinjection.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'headername': {
                'default': 'X-Fuglu-Redirect',
                'description': 'name of header indicating new recipient',
            },
        }

    def examine(self, suspect):
        headername = self.config.get(self.section, 'headername')
        msgrep = suspect.get_message_rep()
        newlhs = msgrep.get(headername, None)

        # get from mime headers
        if newlhs is None and msgrep.is_multipart():
            for part in msgrep.walk():
                newlhs = part.get(headername, None)
                if newlhs is not None:
                    break

        if newlhs is None:
            self.logger.debug(f'{suspect.id} nothing to rewrite')
            return DUNNO

        rcptdom = suspect.to_address.rsplit('@', 1)[-1]
        newrcpt = f'{newlhs}@{rcptdom}'
        self.logger.info(f'{suspect.id} rcpt rewritten from {suspect.to_address} to {newrcpt}')
        suspect.to_address = newrcpt
        suspect.recipients = [newrcpt]
        return DUNNO


class ConditionalRcptAppend(ScannerPlugin):
    """
    Append domain name to recipient based on subject patterns
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'rcpt_append': {
                'default': '',
                'description': 'domain name to append to recipient',
            },
            'subject_rgx': {
                'default': '',
                'description': 'regular expression pattern for subject matches. rewrite only if regex hits.',
            },
            'enable_cond_rewrite': {
                'default': 'False',
                'description': 'enable rewrite feature. can be overriden in dbconfig.',
            },
            'datasource': {
                'default': '',
                'description': """
                            dbconfig
                            tag:filtersettings:enable_cond_rewrite - get from p_blwl FilterSettings backend tag. use ${domain} and ${recipient} in tag name for specific per domain/recipient overrides
                            """,
            },
        }
        self.rgx_cache = {}
    
    def _rewrite_rcpt(self, rcpt, append):
        if not rcpt.endswith(append):
            rcpt = f'{rcpt}{append}'
        return rcpt
    
    def examine(self, suspect):
        rcpt_append = self.config.get(self.section, 'rcpt_append')
        subject_rgx = self.config.get(self.section, 'subject_rgx')
        datasource = self.config.get(self.section, 'datasource')
        if not rcpt_append or not subject_rgx or not datasource:
            return DUNNO
        
        enabled = False
        if datasource == 'dbconfig':
            runtimeconfig = DBConfig(self.config, suspect)
            enabled = runtimeconfig.getboolean(self.section, 'enable_cond_rewrite')
        elif datasource.startswith('tag:'):
            keylist = datasource.split(':')[1:]
            value = suspect.tags.copy()
            for key in keylist:
                if key.startswith('$'):
                    template = _SuspectTemplate(key)
                    key = template.safe_substitute({'recipient': suspect.to_address, 'domain': suspect.to_domain})
                value = value.get(key, {})
                if isinstance(value, (int, float)):
                    enabled = bool(value)
                    break
        if not enabled:
            return DUNNO
        
        rgx = self.rgx_cache.get(subject_rgx)
        if rgx is None:
            rgx = re.compile(subject_rgx, re.I)
            self.rgx_cache[subject_rgx] = rgx
        
        subject = suspect.get_header('subject') or ''
        if subject and rgx.search(subject):
            if not rcpt_append.startswith('.'):
                rcpt_append = f'.{rcpt_append}'
            
            recipients = []
            for rcpt in suspect.recipients:
                newrcpt = self._rewrite_rcpt(rcpt, rcpt_append)
                self.logger.debug(f'{suspect.id} rewrite rcpt {rcpt} to {newrcpt}')
                recipients.append(newrcpt)
            suspect.recipients = recipients
        else:
            self.logger.debug(f'{suspect.id} no rewrite subject tags found')
        return DUNNO
    
    def lint(self):
        if not self.check_config():
            return False
        
        subject_rgx = self.config.get(self.section, 'subject_rgx')
        if subject_rgx:
            try:
                re.compile(subject_rgx, re.I)
            except Exception as e:
                print(f'ERROR: failed to compile regex {subject_rgx} due to {e.__class__.__name__}: {str(e)}')
                return False
            
        datasource = self.config.get(self.section, 'datasource')
        if not datasource:
            print('WARNING: datasource not set, this plugin will do nothing')
        elif not datasource=='dbconfig' or datasource.startswith('tag:'):
            print(f'WARNING: invalid datasource {datasource} - this plugin will do nothing')
        return True


class VirusReject(ScannerPlugin):
    """
    Reject if suspect is marked as virus

    Can be used to delay virus rejects
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
        }
        self.logger = self._logger()

    def __str__(self):
        return "Reject if message is marked as virus"

    def examine(self, suspect: Suspect):
        actioncode = DUNNO
        message = None

        try:
            if suspect.is_virus():
                enginename = [e for e in suspect.tags['virus'] if e][0]
                viruses = suspect.tags[f'{enginename}.virus']
                firstinfected, firstvirusname = list(viruses.items())[0]

                values = dict(infectedfile=firstinfected, virusname=firstvirusname)
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
                actioncode = REJECT
        except Exception as e:
            self.logger.error(f"{suspect.id} error creating rejectmessage: ({type(e)} {str(e)}")

        return actioncode, message

    def lint(self):
        allok = self.check_config()
        return allok
