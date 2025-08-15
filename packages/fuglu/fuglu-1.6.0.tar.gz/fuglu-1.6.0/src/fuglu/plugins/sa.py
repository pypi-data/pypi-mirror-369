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
from fuglu.shared import ScannerPlugin, DUNNO, Suspect, string_to_actioncode, apply_template, actioncode_to_string
from fuglu.extensions.sql import DBConfig, get_session, SQL_EXTENSION_ENABLED, DeclarativeBase, RESTAPIError
from fuglu.stringencode import force_bString, force_uString
from fuglu.lib.patchedemail import PatchedMessage
import time
import socket
import email
import re
import os
from email.mime.text import MIMEText

GTUBE = """Date: Mon, 08 Sep 2008 17:33:54 +0200
To: oli@unittests.fuglu.org
From: oli@unittests.fuglu.org
Subject: test scanner

  XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X
"""

GLOBALSCOPE = '$GLOBAL'
if SQL_EXTENSION_ENABLED:
    from sqlalchemy import Column
    from sqlalchemy.types import Unicode, Integer

    class UserPref(DeclarativeBase):
        __tablename__ = 'userpref'
        prefid = Column(Integer, primary_key=True)
        username = Column(Unicode(100), nullable=False)
        preference = Column(Unicode(30), nullable=False)
        value = Column(Unicode(100), nullable=False)
        
        def __str__(self):
            return f"<UserPref({self.username}) preference={self.preference} value={self.value}>"
        
        def __repr__(self):
            return str(self)
else:
    UserPref = None


class SAPlugin(ScannerPlugin):

    """This plugin passes suspects to spamassassin daemon.

Prerequisites: SPAMD must be installed and running (not necessarily on the same box as fuglu)

Notes for developers:

if forwardoriginal=False, the message source will be completely replaced with the answer from spamd.

Tags:

 * reads ``SAPlugin.skip``, (boolean) skips scanning if this is True
 * reads ``SAPlugin.tempheader``, (text) prepends this text to the scanned message (use this to pass temporary headers to spamassassin which should not be visible in the final message)
 * sets ``spam['spamassassin']`` (boolean)
 * sets ``SAPlugin.spamscore`` (float) if possible
 * sets ``SAPlugin.skipreason`` (string) if the message was not scanned (fuglu >0.5.0)
 * sets ``SAPlugin.report``, (string) report from spamd or spamheader (where score was found) depending on forwardoriginal setting
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where spamd runs',
            },

            'port': {
                'default': '783',
                'description': "tcp port number or path to spamd unix socket",
            },

            'timeout': {
                'default': '30',
                'description': 'how long should we wait for an answer from sa',
            },

            'maxsize': {
                'default': '256000',
                'description': "maximum size in bytes. larger messages will be skipped (or stripped, see below).",
            },

            'strip_oversize': {
                'default': '1',
                'description': "enable scanning of messages larger than maxsize. all attachments will be stripped and only headers, plaintext and html part will be scanned. If message is still oversize it will be truncated.",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'retry_sleep': {
                'default': '1',
                'description': 'how long should fuglu wait in seconds before retryng the connection',
            },

            'scanoriginal': {
                'default': 'True',
                'description': "should we scan the original message as retreived from postfix or scan the current state \nin fuglu (which might have been altered by previous plugins)\nonly set this to disabled if you have a custom plugin that adds special headers to the message that will be \nused in spamassassin rules",
            },

            'forwardoriginal': {
                'default': 'False',
                'description': """forward the original message or replace the content as returned by spamassassin\nif this is enabled, no spamassassin headers will be visible in the final message.\n"original" in this case means "as passed to spamassassin", eg. if 'scanoriginal' above is disabled this will forward the\nmessage as retreived from previous plugins """,
            },

            'spamheader': {
                'default': 'X-Spam-Status',
                'description': """what header does SA set to indicate the spam status\nNote that fuglu requires a standard header template configuration for spamstatus and score extraction\nif 'forwardoriginal' is set to 0\neg. start with _YESNO_ or _YESNOCAPS_ and contain score=_SCORE_""",
            },

            'spamheader_prepend': {
                'default': 'X-Spam-',
                'description': 'tells fuglu what spamassassin prepends to its headers. Set this according to your spamassassin config especially if you forwardoriginal=0 and strip_oversize=1',
            },

            'peruserconfig': {
                'default': 'True',
                'description': 'enable user_prefs in SA. This hands the recipient address over the spamd connection which allows SA to search for configuration overrides',
            },

            'lowercase_user': {
                'default': 'True',
                'description': 'lowercase user (envelope rcpt) before passing it to spamd'
            },

            'lowspamlevel': {
                'default': '',
                'description': 'spamscore threshold to mark a message as low spam. usually same as required_score in spamassassin config. leave empty to use spamassassin evaluation.',
            },

            'highspamlevel': {
                'default': '15',
                'description': 'spamscore threshold to mark a message as high spam',
            },

            'highspamaction': {
                'default': 'DEFAULTHIGHSPAMACTION',
                'description': "what should we do with high spam (spam score above highspamlevel)",
            },

            'lowspamaction': {
                'default': 'DEFAULTLOWSPAMACTION',
                'description': "what should we do with low spam (eg. detected as spam, but score not over highspamlevel)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'message identified as spam',
                'description': "reject message template if running in pre-queue mode",
            },

            'sql_blocklist_dbconnectstring': {
                'default': '',
                'description': "sqlalchemy db connect string, e.g. mysql:///localhost/spamassassin",
            },

            'attach_suspect_tags': {
                'default': '',
                'description': "Suspect tags to attach as text part to message for scanning",
            },

            'oversize_attach_suspect_tags': {
                'default': '',
                'description': "Suspect tags to attach as text part to message for scanning if message "
                               "has been stripped due to size",
            },

            'original_sender_header': {
                'default': '',
                'description': 'use original sender from this header instead of suspect.from_address'
            },

        }
        self.logger = self._logger()

    def __str__(self):
        return "SpamAssassin"

    def lint(self):
        allok = self.check_config() and self._lint_ping() and self._lint_spam() and self._lint_blocklist()
        return allok

    def _lint_blocklist(self):
        dbconnectionstring = self.config.get(self.section, 'sql_blocklist_dbconnectstring')
        if not dbconnectionstring:
            return True

        if not SQL_EXTENSION_ENABLED:
            print("SQL Blacklist requested but SQLALCHEMY is not enabled")
            return False

        suspect = Suspect('dummy@example.com', 'dummy@example.com', '/dev/null')
        try:
            self._get_sql_blocklist(suspect)
            print("SQL UserPref blocklist query OK")
            return True
        except Exception as e:
            print("SQL UserPref blocklist query failed: %s" % str(e))
            return False

    def _lint_ping(self):
        """ping sa"""
        retries = self.config.getint(self.section, 'retries')
        retry_sleep = self.config.getint(self.section, 'retry_sleep')
        for i in range(0, retries):
            try:
                self.logger.debug('Contacting spamd (Try %s of %s)' % (i + 1, retries))
                s = self.__init_socket()
                s.sendall(b'PING SPAMC/1.2')
                s.sendall(b"\r\n")
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line = force_uString(socketfile.readline())
                line = line.strip()
                answer = line.split()
                if len(answer) != 3:
                    print("Invalid SPAMD PONG: %s" % line)
                    return False

                if answer[2] != "PONG":
                    print("Invalid SPAMD Pong: %s" % line)
                    return False
                print("Got: %s" % line)
                return True
            except socket.timeout:
                print('SPAMD Socket timed out.')
            except socket.herror as h:
                print('SPAMD Herror encountered : %s' % str(h))
            except socket.gaierror as g:
                print('SPAMD gaierror encountered: %s' % str(g))
            except socket.error as e:
                print('SPAMD socket error: %s' % str(e))

            time.sleep(retry_sleep)
        return False

    def _lint_spam(self):
        values = self.safilter_symbols(GTUBE, 'test', fid="<no-suspect>")
        if values is None or len(values) != 3:
            print(f'Invalid SPAMD response to GTUBE: {values}')
            return False

        spamflag, score, rules = values
        if 'GTUBE' in rules:
            print("GTUBE Has been detected correctly")
            return True
        else:
            print("SA did not detect GTUBE")
            return False

    def _get_sql_blocklist(self, suspect: Suspect):
        dbconnectionstring = self.config.get(self.section, 'sql_blocklist_dbconnectstring')
        if not dbconnectionstring:
            return []
        dbsession = get_session(dbconnectionstring)
        query = dbsession.query(UserPref)
        query = query.filter(UserPref.preference.in_(['blacklist_from', 'blocklist_from']))
        scopes = [
            '$GLOBAL',
            f'%{suspect.to_domain}',  # sa domain wide
            f'*@{suspect.to_domain}',  # roundcube sauserprefs plugin
            suspect.to_address,
        ]
        query = query.filter(UserPref.username.in_(scopes))
        results = query.all()
        return results

    def check_sql_blocklist(self, suspect, runtimeconfig=None):
        """Check this message against the SQL blocklist. returns highspamaction on hit, DUNNO otherwise"""

        action = DUNNO
        message = None
        if not SQL_EXTENSION_ENABLED:
            self.logger.error('Cannot check sql blocklist, SQLALCHEMY extension is not available')
            return action, message

        try:
            blocklistings = self._get_sql_blocklist(suspect)
        except Exception as e:
            self.logger.error(f'{suspect.id} Could not read UserPrefs: {e.__class__.__name__}: {str(e)}')
            action = self._problemcode()
            message = 'Internal Server Error'
            return action, message

        for result in blocklistings:
            self.logger.debug(f'{suspect.id} checking blocklist value {result.value}')
            # build regex
            # translate glob to regexr
            # http://stackoverflow.com/questions/445910/create-regex-from-glob-expression
            regexp = re.escape(result.value).replace(r'\?', '.').replace(r'\*', '.*?')
            self.logger.debug(regexp)
            pattern = re.compile(regexp)

            if pattern.search(suspect.from_address):
                self.logger.debug(f'{suspect.id} Blocklist match : {suspect.from_address} for sa pref {result.value}')
                confcheck = self.config
                if runtimeconfig is not None:
                    confcheck = runtimeconfig
                try:
                    action = string_to_actioncode(confcheck.get(self.section, 'highspamaction'), self.config)
                    values = dict(spamscore='n/a')
                    message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
                except RESTAPIError as e:
                    action = self._problemcode()
                    self.logger.warning(f'{suspect.id} {actioncode_to_string(action)} due to RESTAPIError: {str(e)}')
                    message = 'Internal Server Error'
                highspamlevel = self.config.getfloat(self.section, 'highspamlevel')
                self._spamreport(suspect, True, True, None, highspamlevel, enginename='SpamAssassin')
                prependheader = self.config.get('main', 'prependaddedheaders')
                suspect.add_header(f"{prependheader}Blacklisted", result.value)  # deprecated
                suspect.add_header(f"{prependheader}Blocklisted", result.value)
                suspect.debug(f'{suspect.id} Sender is Blocklisted: {result.value}')

        return action, message
    
    _re_yes = re.compile(r'^YES', re.IGNORECASE)
    _re_score = re.compile(r'Score=([\-\d.]{1,10})', re.IGNORECASE)
    def _extract_spamstatus(self, msgrep, spamheadername, suspect):
        """
        extract spamstatus and score from messages returned by spamassassin
        Assumes a default spamheader configuration, e.g.
        add_header spam Flag _YESNOCAPS_
        or
        add_header all Status _YESNO_, score=_SCORE_ required=_REQD_ tests=_TESTS_ autolearn=_AUTOLEARN_ version=_VERSION_

        :param msgrep: email.message.Message object built from the returned source
        :param spamheadername: name of the header containing the status information
        :return: tuple isspam,spamscore . isspam is a boolean, spamscore a float or None if the spamscore can't be extracted
        """
        isspam = False
        spamheader = msgrep[spamheadername]

        spamscore = None
        if spamheader is None:
            self.logger.warning(f'{suspect.id} Did not find Header {spamheadername} in returned message from SA')
        else:
            if self._re_yes.match(spamheader.strip()) is not None:
                isspam = True

            m = self._re_score.search(spamheader)

            if m is not None:
                spamscore = float(m.group(1))
                self.logger.debug(f'{suspect.id} Spamscore: {spamscore}')
                suspect.debug(f'Spamscore: {spamscore}')
            else:
                self.logger.warning(f'{suspect.id} Could not extract spam score from header: {spamheader}')
                suspect.debug('Could not read spam score from header {spamheader}')
            return isspam, spamscore, spamheader
        return isspam, spamscore, spamheader

    def _get_content(self, suspect):
        maxsize = self.config.getint(self.section, 'maxsize')

        if self.config.getboolean(self.section, 'scanoriginal'):
            content = suspect.get_original_source()
        else:
            content = suspect.get_source()

        # keep copy of original content before stripping
        content_orig = content

        stripped = False
        if suspect.size > maxsize:
            stripped = True
            # send maxsize-1 to be consistent with previous implementation
            content = suspect.source_stripped_attachments(content=content, maxsize=maxsize - 1, with_mime_headers=True)
            suspect.set_tag('SAPlugin.stripped', True)  # deprecated
            suspect.set_tag('SpamAssassin.stripped', True)
            suspect.write_sa_temp_header('X-Fuglu-OrigSize', str(len(content_orig)))
            self.logger.info(f'{suspect.id} stripped attachments, body size reduced from {len(content_orig)} to {len(content)} bytes')
        # stick to bytes
        content = force_bString(content)

        # write fugluid
        suspect.write_sa_temp_header('X-Fuglu-Suspect', str(suspect.id))

        # prepend temporary headers set by other plugins
        tempheaders = suspect.get_sa_temp_headers()
        if tempheaders != b'':
            content = tempheaders + content

        # add incoming port information
        try:
            portheader = b'X-Fuglu-Incomingport: %i\r\n' % int(suspect.get_tag('incomingport', 0))
            content = portheader + content
        except (TypeError, ValueError) as e:
            self.logger.error(f'{suspect.id} could not add incomingport header: {str(e)}')

        # add envelope sender information
        msgrep = suspect.get_message_rep()
        if not 'Return-Path' in msgrep.keys():
            original_sender_header = self.config.get(self.section, 'original_sender_header')
            if original_sender_header and original_sender_header in msgrep:
                from_address = msgrep[original_sender_header] or '<>'
            else:
                from_address = suspect.from_address or '<>'  # bounce address should be <>
            content = force_bString(f'Return-Path: {from_address}\r\n') + content
            self.logger.info(f'{suspect.id} Set temp Return-Path header as {from_address}')
        else:
            self.logger.debug(f'{suspect.id} Return-Path already set as {msgrep["Return-Path"]}')

        extralines = self._text_from_tags(suspect=suspect, stripped=stripped)
        if extralines:
            msgrep = email.message_from_bytes(content, _class=PatchedMessage)
            if msgrep.is_multipart():
                msgrep.attach(MIMEText("\n".join(extralines)))
                content = msgrep.as_bytes()
            else:
                content += b"\r\n" + b"\r\n".join(force_bString(extralines))

            nadd_header = b'X-Fuglu-XTRA: %i\r\n' % len(extralines)
            content = nadd_header + content

        return content, content_orig, stripped

    @staticmethod
    def _getlist_space_comma_separated(inputstring):
        """Create list from string, splitting at ',' space"""
        finallist = []
        if inputstring:
            inputstring = inputstring.strip()
            if inputstring:
                # check for comma-separated list
                commaseplist = [tag.strip() for tag in inputstring.split(',') if tag.strip()]
                # also handle space-separated list
                for tag in commaseplist:
                    # take elements, split by spac
                    finallist.extend([t.strip() for t in tag.split(' ') if t.strip()])
        return finallist

    def _text_from_tags(self, suspect, stripped: bool = False):
        """Collect lines to append from given tags"""
        lines = []
        appendtags = self.config.get(self.section, 'attach_suspect_tags')
        try:
            tags = Suspect.getlist_space_comma_separated(appendtags)
        except Exception:
            tags = []

        oversize_tags = []
        if stripped:
            oversize_appendtags = self.config.get(self.section, 'oversize_attach_suspect_tags')
            try:
                oversize_tags = Suspect.getlist_space_comma_separated(oversize_appendtags)
            except Exception:
                pass

        # make unique list
        tagnames = list(set(tags + oversize_tags))

        for tagname in tagnames:
            tag = force_uString(suspect.get_tag(tagname, []))
            if isinstance(tag, set):
                tag = list(tag)
            elif not isinstance(tag, list):
                tag = [tag]
            lines.extend(tag)
            self.logger.debug(f"{suspect.id} Got {len(tag)} additional lines from suspect tag {tagname}: {tag}")
        return lines

    def examine(self, suspect):
        # check if someone wants to skip sa checks
        if suspect.get_tag('SAPlugin.skip') is True or suspect.get_tag('SpamAssassin.skip') is True:
            self.logger.debug(f'{suspect.id} Skipping SA Plugin (requested by previous plugin)')
            suspect.set_tag('SAPlugin.skipreason', 'requested by previous plugin')  # deprecated
            suspect.set_tag('SpamAssassin.skipreason', 'requested by previous plugin')
            return DUNNO

        runtimeconfig = DBConfig(self.config, suspect)

        maxsize = self.config.getint(self.section, 'maxsize')
        strip_oversize = self.config.getboolean(self.section, 'strip_oversize')

        if suspect.size > maxsize and not strip_oversize:
            self.logger.info(f'{suspect.id} Size Skip, {suspect.size} > {maxsize}')
            suspect.debug('Too big for spamchecks. {suspect.size} > {maxsize}')
            prependheader = self.config.get('main', 'prependaddedheaders')
            suspect.add_header(f"{prependheader}SA-SKIP", f'Too big for spamchecks. {suspect.size} > {maxsize}')
            suspect.set_tag('SAPlugin.skipreason', 'size skip')  # deprecated
            suspect.set_tag('SpamAssassin.skipreason', 'size skip')
            return self.check_sql_blocklist(suspect)

        content, content_orig, stripped = self._get_content(suspect)

        forwardoriginal = self.config.getboolean(self.section, 'forwardoriginal')
        if forwardoriginal:
            ret = self.safilter_report(content, suspect.to_address, fid=suspect.id)
            if ret is None:
                suspect.debug('SA report Scan failed - please check error log')
                self.logger.warning(f'{suspect.id} SA report scan FAILED')
                prependheader = self.config.get('main', 'prependaddedheaders')
                suspect.add_header(f"{prependheader}SA-SKIP", 'SA scan failed')
                suspect.set_tag('SAPlugin.skipreason', 'scan failed')  # deprecated
                suspect.set_tag('SpamAssassin.skipreason', 'scan failed')
                return self._problemcode()
            isspam, spamscore, report = ret
            suspect.tags['SAPlugin.report'] = report  # deprecated

        else:
            filtered = self.safilter(content, suspect.to_address, fid=suspect.id)
            if filtered is None:
                suspect.debug('SA Scan failed - please check error log')
                self.logger.error(f'{suspect.id} SA scan FAILED')
                prependheader = self.config.get('main', 'prependaddedheaders')
                suspect.add_header(f'{prependheader}SA-SKIP', 'SA scan failed')
                suspect.set_tag('SAPlugin.skipreason', 'scan failed')  # deprecated
                suspect.set_tag('SpamAssassin.skipreason', 'scan failed')
                return self._problemcode()
            else:
                if stripped:
                    # create msgrep of filtered msg
                    msgrep_filtered = email.message_from_bytes(filtered, _class=PatchedMessage)
                    header_new = []
                    for h, v in msgrep_filtered.items():
                        header_new.append(force_uString(h).strip() + ': ' + force_uString(v).strip())
                    # add headers to msg
                    sa_prepend = self.config.get(self.section, 'spamheader_prepend')
                    _re_prepend = re.compile('^' + sa_prepend + '[^:]+: ', re.IGNORECASE)
                    for i in header_new:
                        if sa_prepend == '' or sa_prepend is None:
                            break
                        if _re_prepend.match(i):
                            # in case of stripped msg add header to original content
                            content_orig = force_bString(i) + b'\r\n' + force_bString(content_orig)
                        else:
                            continue
                    content = content_orig
                else:
                    content = filtered

            if isinstance(content, str):
                newmsgrep = email.message_from_string(content, _class=PatchedMessage)
            else:
                newmsgrep = email.message_from_bytes(content, _class=PatchedMessage)

            # if original content is forwarded there's no need to reset the attachmant
            # manager. Only header have been changed.
            suspect.set_source(content, att_mgr_reset=(not forwardoriginal))
            spamheadername = self.config.get(self.section, 'spamheader')
            isspam, spamscore, report = self._extract_spamstatus(newmsgrep, spamheadername, suspect)
            suspect.tags['SAPlugin.report'] = report  # deprecated
            self.logger.debug(f'{suspect.id} sa result spam={isspam} score={spamscore} report={report}')

        action = DUNNO
        message = None
        try:
            islowspam = self._is_lowspam(suspect, runtimeconfig, spamscore, isspam)
            ishighspam = self._is_highspam(suspect, runtimeconfig, spamscore)
            if islowspam or ishighspam:
                values = dict(spamscore=spamscore)
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)

            if islowspam and not ishighspam:
                self.logger.debug(f'{suspect.id} Message is spam')
                suspect.debug('Message is spam')
                configaction = string_to_actioncode(runtimeconfig.get(self.section, 'lowspamaction'), self.config)
                if configaction is not None:
                    action = configaction
            elif ishighspam:
                self.logger.debug(f'{suspect.id} Message is highspam')
                suspect.debug('Message is highspam')
                configaction = string_to_actioncode(runtimeconfig.get(self.section, 'highspamaction'), self.config)
                if configaction is not None:
                    action = configaction
            elif not islowspam and not ishighspam:
                self.logger.debug(f'{suspect.id} Message is not spam (isspam={isspam} islowspam={islowspam} ishighspam={ishighspam})')
                suspect.debug('Message is not spam')

            if spamscore is not None:
                suspect.tags['SAPlugin.spamscore'] = spamscore  # deprecated

            self._spamreport(suspect, islowspam, ishighspam, report, spamscore, enginename='SpamAssassin')
        except RESTAPIError as e:
            self.logger.warning(f'{suspect.id} failed to query REST API: {str(e)}')
            action = self._problemcode()
            message = 'Internal Server Error'

        return action, message

    def _is_lowspam(self, suspect, runtimeconfig, spamscore, isspam):
        if spamscore is not None:
            lowspamlevel = suspect.get_tag('filtersettings', {}).get('lowspamlevel', None)
            if lowspamlevel is None:
                lvl = runtimeconfig.get(self.section, 'lowspamlevel')
                try:
                    lowspamlevel = float(lvl)
                except (TypeError, ValueError):
                    lowspamlevel = None
            if lowspamlevel is None:
                return isspam
            if lowspamlevel is not None and spamscore >= lowspamlevel:
                self.logger.debug(f'{suspect.id} overriding lowspam state: isspam={isspam} spamscore={spamscore} threshold={lowspamlevel}')
                return True
        return False

    def _is_highspam(self, suspect, runtimeconfig, spamscore):
        if spamscore is not None:
            highspamlevel = suspect.get_tag('filtersettings', {}).get('highspamlevel', None)
            if highspamlevel is None:
                highspamlevel = runtimeconfig.getfloat(self.section, 'highspamlevel')
            if spamscore >= highspamlevel:
                return True
        return False

    def __init_socket(self):
        unixsocket = False

        try:
            self.config.getint(self.section, 'port')
        except ValueError:
            unixsocket = True

        if unixsocket:
            sock = self.config.get(self.section, 'port')
            if not os.path.exists(sock):
                raise socket.error(f"unix socket {sock} not found")
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(self.config.getint(self.section, 'timeout'))
            try:
                s.connect(sock)
            except socket.error:
                raise socket.error(f'Could not reach spamd using unix socket {sock}')
        else:
            host = self.config.get(self.section, 'host', resolve_env=True)
            port = self.config.getint(self.section, 'port')
            timeout = self.config.getfloat(self.section, 'timeout')
            try:
                s = socket.create_connection((host, port), timeout)
            except socket.error:
                raise socket.error(f'Could not reach spamd using network ({host}, {port})')

        return s

    def safilter(self, messagecontent, user, fid: str = ""):
        """pass content to sa, return sa-processed mail"""
        retries = self.config.getint(self.section, 'retries')
        retry_sleep = self.config.getint(self.section, 'retry_sleep')
        peruserconfig = self.config.getboolean(self.section, 'peruserconfig')
        if self.config.getboolean(self.section, 'lowercase_user'):
            user = user.lower()
        spamsize = len(messagecontent)
        attempts = retries
        while attempts:
            attempts -= 1
            try:
                self.logger.debug(f'{fid} Contacting spamd  (Try {retries - attempts} of {retries})')
                s = self.__init_socket()
                s.sendall(force_bString('PROCESS SPAMC/1.2'))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(f"Content-length: {spamsize}"))
                s.sendall(force_bString("\r\n"))
                if peruserconfig:
                    s.sendall(force_bString(f"User: {user}"))
                    s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(messagecontent))
                self.logger.debug(f'{fid} Sent {spamsize} bytes to spamd')
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line1_info = socketfile.readline()
                line1_info = force_uString(line1_info)  # convert to unicode string
                self.logger.debug(line1_info)
                line2_contentlength = socketfile.readline()
                line3_empty = socketfile.readline()
                if line3_empty and line3_empty != b'\r\n':
                    self.logger.debug(f'{fid} expected empty line, but spamd sent "{line3_empty.decode()}"')
                content = socketfile.read()
                self.logger.debug(f'{fid} Got {len(content)} message bytes from back from spamd. spamd reported {line2_contentlength.decode()}')
                answer = line1_info.strip().split()
                if len(answer) != 3:
                    self.logger.warning(f"{fid} Got invalid status line from spamd: {line1_info.decode()}")
                    if attempts:
                        time.sleep(retry_sleep)
                    continue

                version, number, status = answer
                if status != 'EX_OK':
                    self.logger.error(f"{fid} Got bad status from spamd: {status}")
                    if attempts:
                        time.sleep(retry_sleep)
                    continue
                attempts = 0
                return content
            except socket.timeout:
                msg = f'{fid} SPAMD Socket timed out (Try {retries - attempts} of {retries}).'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.herror as h:
                msg = f'{fid} SPAMD Herror encountered (Try {retries - attempts} of {retries}): {str(h)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.gaierror as g:
                msg = f'{fid} SPAMD gaierror encountered (Try {retries - attempts} of {retries}): {str(g)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.error as e:
                msg = f'{fid} SPAMD socket error (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except ConnectionRefusedError as e:
                msg = f'{fid} SPAMD connection refused (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except Exception as e:
                msg = f'{fid} SPAMD communication error (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg, exc_info=e)

            if attempts:
                time.sleep(retry_sleep)
        return None

    def safilter_symbols(self, messagecontent, user, fid: str = ""):
        """Pass content to sa, return spamflag, score, rules"""
        ret = self._safilter_content(messagecontent, user, 'SYMBOLS', fid=fid)
        if ret is None:
            return None

        status, score, content = ret

        content = force_uString(content)
        rules = content.split(',')
        return status, score, rules

    def safilter_report(self, messagecontent, user, fid: str = ""):
        return self._safilter_content(messagecontent, user, 'REPORT', fid=fid)

    def _safilter_content(self, messagecontent, user, command, fid: str = ""):
        """pass content to sa, return body"""
        assert command in ['SYMBOLS', 'REPORT', ]
        retries = self.config.getint(self.section, 'retries')
        retry_sleep = self.config.getint(self.section, 'retry_sleep')
        peruserconfig = self.config.getboolean(self.section, 'peruserconfig')
        if self.config.getboolean(self.section, 'lowercase_user'):
            user = user.lower()
        spamsize = len(messagecontent)
        attempts = retries
        while attempts:
            attempts -= 1
            try:
                self.logger.debug(f'{fid} Contacting spamd  (Try {retries - attempts} of {retries})')
                s = self.__init_socket()
                s.sendall(force_bString(f'{command} SPAMC/1.2'))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(f"Content-length: {spamsize}"))
                s.sendall(force_bString("\r\n"))
                if peruserconfig:
                    s.sendall(force_bString(f"User: {user}"))
                    s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(messagecontent))
                self.logger.debug(f'{fid} Sent {spamsize} bytes to spamd')
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line1_info = force_uString(socketfile.readline())
                self.logger.debug(f"{fid} Answer line1: {line1_info}")
                line2_spaminfo = force_uString(socketfile.readline())

                line3_empty = socketfile.readline()
                if line3_empty and line3_empty != b'\r\n':
                    self.logger.debug(f'{fid} expected empty line, but spamd sent "{line3_empty}"')
                content = socketfile.read()
                content = content.strip()

                self.logger.debug(f'{fid} Got {len(content)} message bytes from back from spamd')
                answer = line1_info.strip().split()
                if len(answer) != 3:
                    self.logger.warning(f"{fid} Got invalid status line from spamd: {line1_info}")
                    if attempts:
                        time.sleep(retry_sleep)
                    continue

                version, number, status = answer
                if status != 'EX_OK':
                    self.logger.error(f"{fid} Got bad status from spamd: {status}")
                    if attempts:
                        time.sleep(retry_sleep)
                    continue

                self.logger.debug(f'{fid} Spamd said: {line2_spaminfo}')
                spamword, spamstatusword, colon, score, slash, required = line2_spaminfo.split()
                spstatus = False
                if spamstatusword == 'True':
                    spstatus = True
                attempts = 0
                return spstatus, float(score), content
            except socket.timeout:
                msg = f'{fid} SPAMD Socket timed out (Try {retries - attempts} of {retries}).'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.herror as h:
                msg = f'{fid} SPAMD Herror encountered (Try {retries - attempts} of {retries}): {str(h)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.gaierror as g:
                msg = f'{fid} SPAMD gaierror encountered (Try {retries - attempts} of {retries}): {str(g)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except socket.error as e:
                msg = f'{fid} SPAMD socket error (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except ConnectionRefusedError as e:
                msg = f'{fid} SPAMD connection refused (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg)
            except Exception as e:
                msg = f'{fid} SPAMD communication error (Try {retries - attempts} of {retries}): {str(e)}'
                self.logger.warning(msg) if attempts else self.logger.error(msg, exc_info=e)

            if attempts:
                time.sleep(retry_sleep)
        return None

    def debug_proto(self, messagecontent, command='SYMBOLS'):
        """proto debug... only used for development"""
        command = command.upper()
        assert command in ['CHECK', 'SYMBOLS', 'REPORT',
                           'REPORT_IFSPAM', 'SKIP', 'PING', 'PROCESS', 'TELL']

        host = "127.0.0.1"
        port = 783
        timeout = 20

        spamsize = len(messagecontent)

        s = socket.create_connection((host, port), timeout)
        s.sendall(command.encode() + b' SPAMC/1.2')
        s.sendall(b"\r\n")
        s.sendall(b"Content-length: " + str(spamsize).encode())
        s.sendall(b"\r\n")
        s.sendall(b"\r\n")
        s.sendall(messagecontent)
        s.shutdown(socket.SHUT_WR)
        socketfile = s.makefile("rb")
        gotback = socketfile.read()
        print(gotback)


SALEARN_LOCAL = 'local'
SALEARN_REMOTE = 'remote'
SALEARN_HAM = 'ham'
SALEARN_SPAM = 'spam'
SALEARN_SET = 'Set'
SALEARN_REMOVE = 'Remove'


class SALearn(SAPlugin):
    """This plugin passes suspects to spamassassin daemon (bayes learning/unlearning only).

Prerequisites: SPAMD must be installed and running (not necessarily on the same box as fuglu)

Tags:

 * reads ``salearn.class``, (text or None) set to 'ham' or 'spam' for learning, any other value will disable learning
 * reads ``SAPlugin.action``, (text) set to 'Set' or 'Remove' for respective action. If unset, defaults to 'Set'.
"""

    def __init__(self, config, section):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where spamd runs',
            },

            'port': {
                'default': '783',
                'description': "tcp port number or path to spamd unix socket",
            },

            'timeout': {
                'default': '30',
                'description': 'how long should we wait for an answer from sa',
            },

            'maxsize': {
                'default': '256000',
                'description': "maximum size in bytes. larger messages will be skipped",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'peruserconfig': {
                'default': 'True',
                'description': 'enable user_prefs in SA. This hands the recipient address over the spamd connection which allows SA to search for configuration overrides',
            },

            'problemaction': {
                'default': 'DUNNO',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'learn_local': {
                'default': 'True',
                'description': 'learn to local database',
            },

            'learn_remote': {
                'default': 'True',
                'description': 'learn to remote database',
            },

            'learn_default': {
                'default': SALEARN_SPAM,
                'description': 'default learn action (ham, spam or leave empty)'
            }

        }

    def _get_databases(self):
        databases = []
        if self.config.getboolean(self.section, 'learn_local'):
            databases.append(SALEARN_LOCAL)
        if self.config.getboolean(self.section, 'learn_remote'):
            databases.append(SALEARN_REMOTE)
        return databases

    def examine(self, suspect):
        spamsize = suspect.size
        maxsize = self.config.getint(self.section, 'maxsize')

        if spamsize > maxsize:
            self.logger.info('%s Size Skip, %s > %s' % (suspect.id, spamsize, maxsize))
            suspect.debug('Too big for spamchecks. %s > %s' % (spamsize, maxsize))
            return DUNNO

        messageclass = suspect.get_tag('salearn.class', self.config.get(self.section, 'learn_default'))
        learnaction = suspect.get_tag('salearn.action', SALEARN_SET)

        if messageclass not in [SALEARN_SPAM, SALEARN_HAM]:
            self.logger.debug('%s not learning message, message class tag value=%s' % (suspect.id, messageclass))
        else:
            databases = self._get_databases()
            ret = self._salearn_content(suspect.get_original_source(), suspect.to_address, messageclass, learnaction, databases)
            if not ret:
                return self._problemcode()
        return DUNNO

    def _salearn_content(self, messagecontent, user, messageclass=SALEARN_SPAM, learnaction=SALEARN_SET, databases=(SALEARN_LOCAL, SALEARN_REMOTE)):
        """pass content to sa, return body"""
        assert messageclass in [SALEARN_HAM, SALEARN_SPAM]
        assert learnaction in [SALEARN_SET, SALEARN_REMOVE]
        assert 1 <= len(databases) <= 2
        for db in databases:
            assert db in [SALEARN_LOCAL, SALEARN_REMOTE]

        retries = self.config.getint(self.section, 'retries')
        peruserconfig = self.config.getboolean(self.section, 'peruserconfig')
        if self.config.getboolean(self.section, 'lowercase_user') and user:
            user = user.lower()
        spamsize = len(messagecontent)
        for i in range(0, retries):
            try:
                self.logger.debug('Contacting spamd  (Try %s of %s)' % (i + 1, retries))
                s = self.__init_socket()
                s.sendall(force_bString('TELL SPAMC/1.2'))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("Content-length: %s" % spamsize))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("Message-class: %s" % messageclass))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("%s: %s" % (learnaction, ', '.join(databases))))
                s.sendall(force_bString("\r\n"))
                if peruserconfig:
                    s.sendall(force_bString("User: %s" % user))
                    s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(messagecontent))
                self.logger.debug('Sent %s bytes to spamd' % spamsize)
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line1_info = force_uString(socketfile.readline())
                self.logger.debug(f"Answer line1: {line1_info}")
                line2_spaminfo = force_uString(socketfile.readline())

                answer = line1_info.strip().split()
                if len(answer) != 3:
                    self.logger.warning("Got invalid status line from spamd: %s" % line1_info)
                    continue

                version, number, status = answer
                if status != 'EX_OK':
                    self.logger.error("Got bad status from spamd: %s" % status)
                    continue

                self.logger.debug('Spamd said: %s' % line2_spaminfo)
                hdr, status = line2_spaminfo.split(':')
                if (learnaction == SALEARN_SET and hdr == 'DidSet') \
                        or (learnaction == SALEARN_REMOVE and hdr == 'DidRemove'):
                    success = True
                else:
                    success = False

                return success
            except socket.timeout:
                self.logger.error('SPAMD Socket timed out.')
            except socket.herror as h:
                self.logger.error('SPAMD Herror encountered : %s' % str(h))
            except socket.gaierror as g:
                self.logger.error('SPAMD gaierror encountered: %s' % str(g))
            except socket.error as e:
                self.logger.error('SPAMD socket error: %s' % str(e))
            except Exception as e:
                self.logger.error('SPAMD communication error: %s' % str(e), exc_info=e)

            time.sleep(1)
        return None

    def lint(self):
        allok = self.check_config() and self._lint_ping()
        if allok:
            databases = self._get_databases()
            allok = 1 <= len(databases) <= 2
            if not allok:
                print('ERROR: Enable at least one of learn_local, learn_remote')
        return allok


if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:
        print('need command argument')
        sys.exit(1)
    plugin = SAPlugin(None)
    print("sending...")
    print("--------------")
    plugin.debug_proto(GTUBE, sys.argv[1])
    print("--------------")
