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
import os
import imaplib
import smtplib
import fnmatch
import time
import asyncio
import re
import typing as tp
from urllib.parse import urlparse
from fuglu.shared import ScannerPlugin, DUNNO, DELETE, SuspectFilter, AppenderPlugin, Suspect, get_outgoing_helo, \
    apply_template, FileList, deprecated, actioncode_to_string, string_to_actioncode
from fuglu.stringencode import force_uString
from fuglu.bounce import FugluSMTPClient, FugluAioSMTPClient, HAVE_AIOSMTP, SMTPException, Bounce
from fuglu.plugins.ratelimit.helperfuncs import get_ptr
from fuglu.asyncprocpool import get_event_loop

try:
    from domainmagic.mailaddr import email_normalise_ebl
    from domainmagic.validators import is_ipv6
    HAVE_DOMAINMAGIC=True
except ImportError:
    def is_ipv6(value):
        return value and ':' in value
    def email_normalise_ebl(value):
        return value.lower()
    HAVE_DOMAINMAGIC=False


# TODO: reuse imap connections
#TODO: retries

class IMAPCopyPlugin(ScannerPlugin):
    """This plugin stores a copy of the message to an IMAP mailbox if it matches certain criteria (Suspect Filter).
The rulefile works similar to the archive plugin. As third column you have to provide imap account data in the form:

<protocol>://<username>:<password>@<servernameorip>[:port]/<mailbox>

<protocol> is one of:
 - imap (port 143, no encryption)
 - imap+tls (port 143 and StartTLS, only supported in Python 3)
 - imaps (port 993 and SSL)


"""

    def __init__(self, config, section=None):
        super().__init__(config, section)

        self.requiredvars = {
            'imapcopyrules': {
                'default': '${confdir}/imapcopy.regex',
                'description': 'IMAP copy suspectFilter File',
            },

            'storeoriginal': {
                'default': 'True',
                'description': "if true/1/yes: store original message\nif false/0/no: store message probably altered by previous plugins, eg with spamassassin headers",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
        }
        self.filter = None
        self.logger = self._logger()

    def examine(self, suspect: Suspect):
        try:
            action = self._run(suspect)
            message = None
        except Exception as e:
            self.logger.error(f'{suspect.id} failed to copy to imap server due to {e.__class__.__name__}: {str(e)}')
            action, message = self._problemcode()
        return action, message

    def process(self, suspect: Suspect, decision):
        try:
            action = self._run(suspect)
            if action == DELETE:
                self.logger.warning(f'{suspect.id} imapcopy rule issued DELETE, ignoring in appender plugin (original decision={actioncode_to_string(decision)})')
        except Exception as e:
            self.logger.error(f'{suspect.id} failed to copy to imap server due to {e.__class__.__name__}: {str(e)}')

    def _run(self, suspect: Suspect):
        imapcopyrules = self.config.get(self.section, 'imapcopyrules')
        if imapcopyrules is None or imapcopyrules == "":
            self.logger.warning(f'{suspect.id} not IMAP copy rules file defined')
            return DUNNO

        if not os.path.exists(imapcopyrules):
            self.logger.error(f'{suspect.id} IMAP copy rules file does not exist: {imapcopyrules}')
            return DUNNO

        if self.filter is None:
            self.filter = SuspectFilter(imapcopyrules)

        match, info = self.filter.matches(suspect, extended=True)
        if match:
            delete = False
            if info.arg is not None and info.arg.lower() == 'no':
                suspect.debug("Suspect matches imap copy exception rule")
                self.logger.info(f"{suspect.id} Header {info.fieldname} matches imap copy exception rule '{info.pattern}'")
            else:
                if info.arg is None or (not info.arg.lower().startswith('imap') and info.arg.upper() != 'DELETE'):
                    self.logger.error(f"{suspect.id} Unknown target format {info.arg} should be 'imap(s)://user:pass@host/folder'")

                else:
                    self.logger.info(f"{suspect.id} Header {info.fieldname} matches imap copy rule '{info.pattern}'")
                    if suspect.get_tag('debug'):
                        suspect.debug("Suspect matches imap copy rule (I would copy it if we weren't in debug mode)")
                    else:
                        if ' ' not in info.arg:
                            if info.arg.upper() != 'DELETE':
                                self.storeimap(suspect, info.arg)
                            else:
                                self.logger.debug(f'{suspect.id} cannot store. arg={info.arg}')
                                return DUNNO
                        else:
                            for value in info.arg.split():
                                if value.upper() == 'DELETE':
                                    self.logger.info(f"{suspect.id} imap copy rule '{info.pattern}' action DELETE")
                                    delete = True
                                    continue
                                self.storeimap(suspect, value)
                    if delete:
                        return DELETE
        else:
            suspect.debug("No imap copy rule/exception rule applies to this message")
            self.logger.debug(f"{suspect.id} No imap copy rule/exception rule applies to this message")
        return DUNNO

    def imapconnect(self, imapurl: str, lintmode: bool = False, fugluid='n/a'):
        p = urlparse(imapurl)
        scheme = p.scheme.lower()
        host = p.hostname
        port = p.port
        username = p.username
        password = p.password
        folder = p.path[1:]

        if scheme == 'imaps':
            ssl = True
            tls = False
        elif scheme == 'imap+tls':
            ssl = False
            tls = True
        else:
            ssl = False
            tls = False

        if port is None:
            if ssl:
                port = imaplib.IMAP4_SSL_PORT
            else:
                port = imaplib.IMAP4_PORT
        try:
            if ssl:
                imap = imaplib.IMAP4_SSL(host=host, port=port)
            else:
                imap = imaplib.IMAP4(host=host, port=port)
        except Exception as e:
            ltype = 'IMAP'
            if ssl:
                ltype = 'IMAP-SSL'
            msg = f"{ltype} Connection to server {host} failed: {e.__class__.__name__}: {e.args[0]}"
            if lintmode:
                print(msg)
            else:
                self.logger.error(f'{fugluid} {msg}')
            return None

        if tls and hasattr(imap, 'starttls'):
            try:
                msg = imap.starttls()
                if msg[0] != 'OK':
                    if lintmode:
                        print(msg)
                    return None

            except Exception as e:
                if lintmode:
                    print(f'{e.__class__.__name__}: {str(e)}')
                return None

        try:
            imap.login(username, password)
        except Exception as e:
            msg = f"Login to server {host} failed for user {username}: {e.__class__.__name__}: {e.args[0]}"
            if lintmode:
                print(msg)
            else:
                self.logger.error(f'{fugluid} {msg}')
            return None

        try:
            mtype, count = imap.select(folder)
            excmsg = ''
        except Exception as e:
            excmsg = f'{e.__class__.__name__}: {str(e)}'
            mtype = None

        if mtype == 'NO' or excmsg:
            msg = f"Could not select folder {username}@{host}/{folder} : {excmsg}"
            if lintmode:
                print(msg)
            else:
                self.logger.error(f'{fugluid} {msg}')
            return None
        return imap

    def storeimap(self, suspect: Suspect, imapurl: str):
        imap = self.imapconnect(imapurl, False, suspect.id)
        if not imap:
            return
        # imap.debug=4
        p = urlparse(imapurl)
        folder = p.path[1:]

        if self.config.getboolean(self.section, 'storeoriginal'):
            src = suspect.get_original_source()
        else:
            src = suspect.get_source()

        mtype, data = imap.append(folder, None, None, src)
        if mtype != 'OK':
            self.logger.error(f'{suspect.id} Could put store in IMAP {imapurl}. APPEND command failed: {data}')
        else:
            self.logger.debug(f'{suspect.id} stored in {imapurl} as {data}')
        imap.logout()

    def lint(self):
        allok = (self.check_config() and self.lint_imap())
        return allok

    def lint_imap(self):
        # read file, check for all imap accounts
        imapcopyrules = self.config.get(self.section, 'imapcopyrules')
        if imapcopyrules != '' and not os.path.exists(imapcopyrules):
            print(f'ERROR: Imap copy rules file does not exist : {imapcopyrules}')
            return False
        elif not imapcopyrules:
            print(f'ERROR: Imap copy rules file not defined')
            return False
        sfilter = SuspectFilter(imapcopyrules)

        accounts = []
        for rule in sfilter.get_list():
            if rule.args not in accounts:
                if rule.args is None:
                    print(f"Rule {rule.fieldname} {rule.pattern.pattern} has no imap copy target")
                    return False
                if rule.args.lower() == 'no':
                    continue
                elif rule.args.lower() == 'delete':
                    return False
                if ' ' not in rule.args:
                    accounts.append(rule.args)
                else:
                    for value in rule.args.split():
                        if value == 'DELETE':
                            continue
                        accounts.append(value)

        success = True
        for acc in accounts:
            msg = 'OK'
            p = urlparse(acc)
            host = p.hostname
            username = p.username
            folder = p.path[1:]
            try:
                imap = self.imapconnect(acc, lintmode=True)
                if not imap:
                    msg = 'ERROR: Failed to connect'
                    success = False
                else:
                    imap.close()
            except Exception as e:
                msg = f'ERROR: {e.__class__.__name__}: {str(e)}'
            print(f"Checked {username}@{host}/{folder} : {msg}")
        if not success:
            return False

        return True


class FeedList(FileList):
    def __init__(self, *args, **kwargs):
        self.target_servers = []
        self.target_domains = {}
        self.target_globs = {}
        super().__init__(*args, **kwargs)

    def _parse_server_args(self, fields):
        target_str = fields[0]
        target_str = target_str.strip(';')
        host = target_str
        args = {}

        if ';' in target_str:
            values = target_str.split(';')
            host = values[0]
            for val in values[1:]:
                k, v = val.split('=', 1)
                k = k.lower()
                if k in ['port', 'timeout', 'retry']:
                    v = int(v)
                elif k in ['tls', 'xclient']:
                    v = v.lower() in ['yes', 'true', '1', 'on']
                args[k] = v

        if fields[1] == '*':
            exceptions = []
            for item in fields[2:]:
                if item.startswith('!'):
                    exceptions.append(item[1:].lower())
            if exceptions:
                args['exc'] = exceptions
        return host.lower(), args

    def _parse_lines(self, lines):
        target_servers = []
        target_domains = {}
        target_globs = {}

        for line in lines:
            line = self._apply_linefilters(line)
            if not line:
                continue

            fields = line.split()
            if len(fields) == 1:
                self.logger.error(f'not a valid feed defintion: {line}')
                continue

            try:
                server_name, server_args = self._parse_server_args(fields)
            except Exception:
                self.logger.error(f'not a valid server defintion: {fields[0]}')
                continue

            server = (server_name, server_args)
            if fields[1] == '*':
                if server not in target_servers:
                    target_servers.append(server)
            else:
                domains = fields[1:]
                for domain in domains:
                    domain = domain.lower()
                    if domain.startswith('!'):
                        # excludes are not supported in non-wildcard definitions
                        continue
                    elif domain.startswith('*.'):
                        try:
                            if server not in target_globs[domain]:
                                target_globs[domain].append(server)
                        except KeyError:
                            target_globs[domain] = [server]
                    else:
                        try:
                            if server not in target_domains[domain]:
                                target_domains[domain].append(server)
                        except KeyError:
                            target_domains[domain] = [server]

        self.target_servers = target_servers
        self.target_domains = target_domains
        self.target_globs = target_globs
        return []

    def get_targets(self):
        """Returns the current list. If the file has been changed since the last call, it will rebuild the list automatically."""
        if self.filename is not None:
            self._reload_if_necessary()
        return self.target_servers, self.target_domains, self.target_globs


LOGLEVEL_EXTREME = 'extreme'

class MailFeed(AppenderPlugin):
    """Send a copy of a message to a certain target server"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'targetfile': {
                'default': '${confdir}/mailfeeds.txt',
                'description': """file with feed targets.
                format: target.server[;opt=val;opt=val] domain1 domain2 or * for all domains
                possible options: port=587;tls=True;xclient=True;user=user;pass=pass;from=<>;to=*;timeout=30;retry=0
                options tls, xclient, and from will override the global defaults defined in plugin config""",
            },

            'mail_types': {
                'default': 'any',
                'description': 'comma separated list of mail classes to be delivered: any, ham, spam, virus, blocked'
            },
            
            'skip_deleted': {
                'default': 'False',
                'description': 'only in appender stage: skip messages that were marked for deletion'
            },

            'from_address': {
                'default': '<>',
                'description': 'envelope sender to be used. set to <> for empty envelope sender, set to * to use original sender',
            },

            'to_address': {
                'default': '${to_localpart}@${target}',
                'description': 'template for envelope recipient to be used. set to * to use original recipient. will always be set to @target if domain is equals to fuglu hostname',
            },

            'use_tls': {
                'default': 'True',
                'description:': 'always use StartTLS when sending mail'
            },

            'use_xclient': {
                'default': 'False',
                'description:': 'send original client information via XCLIENT command'
            },

            'original_sender_header': {
                'default': 'X-Original-Sender',
                'description': 'add original sender in this header'
            },

            'original_recipient_header': {
                'default': 'X-Original-Recipient',
                'description': 'add original sender in this header'
            },
            
            'verbose_logging': {
                'default': 'False',
                'description:': 'log every smtp transaction detail'
            }

        }

        self.mailfeeds = None

    def _load_mailfeeds(self) -> None:
        if self.mailfeeds is None:
            targetfile = self.config.get(self.section, 'targetfile')
            self.mailfeeds = FeedList(targetfile)

    def _get_xclient_args(self, suspect: Suspect) -> tp.Dict[str, str]:
        args = {}
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo

            if not clientip:
                clientip = '[UNAVAILABLE]'
            elif is_ipv6(clientip):
                clientip = f'IPV6:{clientip}'
            elif clienthostname == 'unknown':  # we have a clientip but no fcrdns client hostname
                clienthostname = suspect.get_tag('xclient-ptr')
                if clienthostname is None:
                    clienthostname = get_ptr(clientip, suspect, verify=True)
                    if clienthostname == 'unknown':
                        clienthostname = '[TEMPUNAVAIL]'
                    elif clienthostname == 'nxdomain':
                        clienthostname = '[UNAVAILABLE]'
                    suspect.set_tag('xclient-ptr', clienthostname)
            if not clienthelo:
                clienthelo = '[UNAVAILABLE]'

            args['HELO'] = clienthelo
            args['ADDR'] = clientip
            args['NAME'] = clienthostname
        return args

    def _log_response(self, prefix:str, response:tp.Union[str, tp.Tuple[str,str]], level:str='debug') -> None:
        iserror = False
        if len(response) == 2:
            msg = force_uString(response[1]).replace("\n", " ").replace("\r", " ")
            logmessage = f'{prefix} got response {response[0]} {msg}'
            try:
                code = int(response[0])
                if not 200 <= code <= 299:
                    iserror = True
            except (TypeError, ValueError):
                pass
        else:
            logmessage = f'{prefix} got response {response}'
            
        if not iserror:
            if level == LOGLEVEL_EXTREME:
                if self.config.getboolean(self.section, 'verbose_logging', fallback=False):
                    level = 'debug'
                else:
                    return
            logger = getattr(self.logger, level)
            logger(logmessage)
        else:
            self.logger.error(logmessage)

    def _get_content(self, suspect: Suspect) -> bytes:
        msg_buffer = suspect.get_source(newline=b'\r\n')
        # prepend header with original sender
        original_sender_header = self.config.get(self.section, 'original_sender_header')
        if original_sender_header:
            msg_buffer = Suspect.prepend_header_to_source(original_sender_header, suspect.from_address, msg_buffer)
        # prepend header with original recipient
        original_recipient_header = self.config.get(self.section, 'original_recipient_header')
        if original_recipient_header:
            msg_buffer = Suspect.prepend_header_to_source(original_recipient_header, suspect.to_address, msg_buffer)
        return msg_buffer

    def _get_errcode_from_exc(self, exc:Exception, to_address:str) -> int:
        errcode = 0
        if isinstance(exc.args[0], dict):
            smtperr = exc.args[0].get(to_address)
            if smtperr:
                errcode = smtperr[0]
        return errcode

    def _send_sync(self, suspect: Suspect, target_host: str, target_args: tp.Dict[str, tp.List[str]], from_address: str, to_address: str, retry: int = 3):
        try:
            port = target_args.get('port', smtplib.SMTP_PORT)
            timeout = target_args.get('timeout', 60)
            helostring = get_outgoing_helo(self.config)
            smtp_server = FugluSMTPClient(target_host, port=port, timeout=timeout, local_hostname=helostring)
            use_tls = target_args.get('tls', self.config.getboolean(self.section, 'use_tls', fallback=True))
            use_xclient = target_args.get('xclient', self.config.getboolean(self.section, 'use_xclient', fallback=False))
            use_auth = target_args.get('user') and target_args.get('pass')
            if use_tls:
                try:
                    starttls_resp = smtp_server.starttls()
                    self._log_response(f'{suspect.id} sent starttls to {target_host}', starttls_resp, level=LOGLEVEL_EXTREME)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error(f'{suspect.id} failed to start tls to target server {target_host} due to: {str(e)}')
            if use_xclient:
                xclient_args = self._get_xclient_args(suspect)
                try:
                    if xclient_args:
                        xclient_resp = smtp_server.xclient(xclient_args)
                        self._log_response(f'{suspect.id} sent xclient args {xclient_args} to {target_host}', xclient_resp, level=LOGLEVEL_EXTREME)
                        xclient_helo = xclient_args.get('HELO')
                        if xclient_helo and xclient_helo != '[UNAVAILABLE]':
                            ehlo_resp = smtp_server.ehlo(xclient_helo)
                            self._log_response(f'{suspect.id} sent xclient ehlo {xclient_helo} to {target_host}', ehlo_resp, level=LOGLEVEL_EXTREME)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error(f'{suspect.id} xclient failed with target server {target_host} due to: {str(e)}')
            if use_auth:
                try:
                    login_resp = smtp_server.login(target_args.get('user'), target_args.get('pass'))
                    self._log_response(f'{suspect.id} sent authentication for user {target_args.get("user")} to {target_host}', login_resp, level=LOGLEVEL_EXTREME)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error(f'{suspect.id} failed to authenticate at target server {target_host} with user {target_args.get("user")} due to: {str(e)}')
            content = self._get_content(suspect)
            fails = smtp_server.sendmail(force_uString(from_address), force_uString(to_address), content)
            sendmail_resp = (smtp_server.lastservercode, smtp_server.lastserveranswer)
            self._log_response(f'{suspect.id} sent message for {to_address} to {target_host}', sendmail_resp, level='info')
            try:
                quit_resp = smtp_server.quit()
                self._log_response(f'{suspect.id} sent quit to {target_host}', quit_resp, level=LOGLEVEL_EXTREME)
            except Exception as e:
                self.logger.debug(f'{suspect.id} error sending quit to {target_host}: {e.__class__.__name__}: {str(e)}')
        except Exception as e:
            #self.logger.error('%s failed to forward to %s due to %s' % (suspect.id, target_host, str(e)))
            errcode = self._get_errcode_from_exc(e, to_address)
            if retry > 0 and not (500 < errcode < 599):
                time.sleep(abs(4-retry)/2)
                fails = self._send_sync(suspect, target_host, target_args, from_address, to_address, retry=retry-1)
            else:
                fails = {to_address: f'{e.__class__.__name__}: {str(e)}'}
        return fails

    @deprecated
    async def _send_async(self, suspect: Suspect, target_host: str, target_args: tp.Dict[str, tp.List[str]], from_address: str, to_address: str, retry: int = 3):
        try:
            port = target_args.get('port', smtplib.SMTP_PORT)
            timeout = target_args.get('timeout', 60)
            helostring = get_outgoing_helo(self.config)
            use_tls = target_args.get('tls', self.config.getboolean(self.section, 'use_tls', fallback=True))
            smtp_server = FugluAioSMTPClient(hostname=target_host, port=port, source_address=helostring, start_tls=use_tls, timeout=timeout)
            conn_resp = await smtp_server.connect()
            self._log_response('%s connected to %s' % (suspect.id, target_host), conn_resp, level=LOGLEVEL_EXTREME)
            use_xclient = target_args.get('xclient', self.config.getboolean(self.section, 'use_xclient', fallback=False))
            use_auth = target_args.get('user') and target_args.get('pass')
            if use_xclient:
                xclient_args = self._get_xclient_args(suspect)
                try:
                    if xclient_args:
                        xclient_resp = await smtp_server.xclient(xclient_args)
                        self._log_response('%s sent xclient args %s to %s' % (suspect.id, xclient_args, target_host), xclient_resp, level=LOGLEVEL_EXTREME)
                        xclient_helo = xclient_args.get('HELO')
                        if xclient_helo and xclient_helo != '[UNAVAILABLE]':
                            ehlo_resp = await smtp_server.ehlo(xclient_helo)
                            self._log_response('%s sent xclient ehlo %s to %s' % (suspect.id, xclient_helo, target_host), ehlo_resp, level=LOGLEVEL_EXTREME)
                except SMTPException as e:
                    self.logger.error('%s xclient failed with target server %s due to: %s' % (suspect.id, target_host, str(e)))
            if use_auth:
                try:
                    login_resp = await smtp_server.login(target_args.get('user'), target_args.get('pass'))
                    self._log_response('%s sent authentication for user %s to %s' % (suspect.id, target_args.get('user'), target_host), login_resp, level=LOGLEVEL_EXTREME)
                except SMTPException as e:
                    self.logger.error('%s failed to authenticate at target server %s with user %s due to: %s' %
                                      (suspect.id, target_host, target_args.get('user'), str(e)))
            content = self._get_content(suspect)
            fails, logmsg = await smtp_server.sendmail(from_address, to_address, content)
            self._log_response('%s sent message for %s to %s' % (suspect.id, to_address, target_host), logmsg, level='info')
            try:
                quit_resp = await smtp_server.quit()
                self._log_response('%s sent quit to %s' % (suspect.id, target_host), quit_resp)
            except Exception as e:
                self.logger.debug('%s error sending quit to %s: %s' % (suspect.id, target_host, str(e)))
        except Exception as e:
            import traceback
            self.logger.error('%s failed to forward to %s due to %s' % (suspect.id, target_host, str(e)))
            self.logger.error(traceback.format_exc())
            if retry > 0:
                await asyncio.sleep(abs(4-retry)/2)
                fails = await self._send_async(suspect, target_host, target_args, from_address, to_address, retry=retry-1)
            else:
                fails = {to_address: str(e)}
        return fails

    def _send_mail(self, target_host: str, target_args: tp.Dict[str, tp.List[str]], suspect: Suspect):
        exceptions = target_args.get('exc', [])
        if suspect.to_domain.lower() in exceptions:
            self.logger.debug(f'{suspect.id} skipping sending to {target_host}')
            return
        
        verbose = self.config.getboolean(self.section, 'verbose_logging', fallback=False)
        if verbose:
            self.logger.debug(f'{suspect.id} to {target_host} with args {target_args}')

        from_address = target_args.get('from', self.config.get(self.section, 'from_address'))
        if from_address == '<>':
            from_address = ''
        elif from_address == '*':
            from_address = suspect.from_address

        to_template = target_args.get('to', self.config.get(self.section, 'to_address'))
        if to_template == '*':
            to_address = suspect.to_address
        else:
            to_address = apply_template(to_template, suspect, {'target': target_host})
        to_user, to_domain = to_address.rsplit('@',1)
        if to_domain.lower() == get_outgoing_helo(self.config):
            to_address = f'{to_user}@{target_host}'
        to_address = to_address.lower()

        retry = target_args.get('retry', 3)
        disable_aiosmtp = self.config.getboolean('performance', 'disable_aiosmtp', fallback=True)
        if HAVE_AIOSMTP and not disable_aiosmtp:
            event_loop = get_event_loop(f'{suspect.id} plugin={self.section}')
            fails = event_loop.run_until_complete(self._send_async(suspect, target_host, target_args, from_address, to_address, retry=retry))
        else:
            fails = self._send_sync(suspect, target_host, target_args, from_address, to_address, retry=retry)

        if not fails and verbose:
            self.logger.debug(f'{suspect.id} for {to_address} forwarded to {target_host}')
        elif fails:
            for rcpt in fails:
                resp = fails[rcpt]
                if hasattr(resp, 'args'):
                    resp = resp.args
                self._log_response(f'{suspect.id} delivery failures to {target_host} for {rcpt}', resp, level='error')

    def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()
        
        if not HAVE_DOMAINMAGIC:
            print('WARNING: domainmagic not available, using some fallback functions with limitations')

        if not self.check_config():
            print(fc.strcolor("ERROR: ", "red"), "config check")
            return False

        if HAVE_AIOSMTP:
            print(fc.strcolor("INFO: ", "blue"), 'aiosmtplib available')

        targetfile = self.config.get(self.section, 'targetfile')
        if not os.path.exists(targetfile):
            print(fc.strcolor("ERROR: ", "red"), f'target file {targetfile} not found')
            return False

        self._load_mailfeeds()
        target_servers, target_domains, target_globs = self.mailfeeds.get_targets()
        print(fc.strcolor("INFO: ", "blue"), f'global feed to servers: {", ".join([s[0] for s in target_servers])}')
        print(fc.strcolor("INFO: ", "blue"), f'forwarding {len(target_domains)} domains')
        print(fc.strcolor("INFO: ", "blue"), f'forwarding {len(target_globs)} glob rules')

        return True

    def _feed(self, suspect: Suspect):
        targets_sent = []
        to_domain = suspect.to_domain.lower()
        to_address = email_normalise_ebl(suspect.to_address)

        mail_types = self.config.getlist(self.section, 'mail_types', lower=True)
        do_send = 'any' in mail_types \
            or 'ham' in mail_types and suspect.is_ham() \
            or 'spam' in mail_types and suspect.is_spam() \
            or 'virus' in mail_types and suspect.is_virus() \
            or 'blocked' in mail_types and suspect.is_blocked()

        if not do_send:
            self.logger.debug(f'{suspect.id} not sending as msg is not in types {", ".join(mail_types)}')
            return

        self._load_mailfeeds()
        target_servers, target_domains, target_globs = self.mailfeeds.get_targets()

        for target_server in target_servers:
            self._send_mail(target_server[0], target_server[1], suspect)
            targets_sent.append(target_server)
        for target_server in target_domains.get(to_domain, []):
            if target_server not in targets_sent:
                self._send_mail(target_server[0], target_server[1], suspect)
                targets_sent.append(target_server)
        for target_server in target_domains.get(to_address, []):
            if target_server not in targets_sent:
                self._send_mail(target_server[0], target_server[1], suspect)
                targets_sent.append(target_server)
        for target_glob in target_globs.keys():
            if fnmatch.fnmatch(to_domain, target_glob):
                for target_server in target_globs[target_glob]:
                    if target_server not in targets_sent:
                        self._send_mail(target_server[0], target_server[1], suspect)
                        targets_sent.append(target_server)
                        
        if self.config.getboolean(self.section, 'verbose_logging', fallback=False):
            self.logger.debug(f'{suspect.id} targets sent: {", ".join(targets_sent)}')

    def examine(self, suspect: Suspect):
        self._feed(suspect)
        return DUNNO

    def process(self, suspect: Suspect, decision):
        if decision == DELETE and self.config.getboolean(self.section, 'skip_deleted', fallback=False):
            self.logger.debug(f'{suspect.id} skipping message due to decision=DELETE')
        else:
            self._feed(suspect)


class AutoReport(AppenderPlugin):
    """
    Send attached and/or direct copy of mail to report addresses.
    Attached copy allows certain templating of wrapper mail body
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'trap_regex': {
                'default': '',
                'description': 'regex to match traps by pattern'
            },

            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },

            'report_recipient': {
                'default': '',
                'description': 'address of report recipient (usually a human)',
            },

            'bounce_sender': {
                'default': '<>',
                'description': 'address of bounce generator. use <> for empty envelope sender',
            },

            'bounce_recipient': {
                'default': '',
                'description': 'address of bounce recipient (usually an automated processing system)',
            },

            'subject_template': {
                'default': 'Spam suspect from ${from_address}',
                'description': 'template of URI to sender account details',
            },

            'original_sender_header': {
                'default': 'X-Original-Sender',
                'description': 'add original sender in this header'
            },

            'message_uri_template': {
                'default': '',
                'description': 'template of URI to log showing message details',
            },

            'sender_search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results by sender',
            },

            'server_search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results by sending server',
            },
        }

    def process(self, suspect, decision):
        culprit = None
        for to_address in suspect.recipients:
            if not self._static_traps(to_address):
                culprit = to_address
        if culprit is None:
            return

        if suspect.is_ham():
            self._send_mail(suspect, culprit)
        self._hash_mail(suspect)
        return

    def _static_traps(self, rcpt):
        is_trap = False
        rgx = self.config.get(self.section, 'trap_regex')
        if rgx and re.search(rgx, rcpt):
            is_trap = True
        return is_trap

    def _send_mail(self, suspect, culprit):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info(f'{suspect.id} not reported because report recipient is not defined')
            return

        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''

        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo
            if clientip and not clienthostname:
                clienthostname = get_ptr(clientip, suspect, verify=True)
        else:
            clienthelo = clientip = clienthostname = None
        
        subject = suspect.decode_msg_header(suspect.get_header('suspect', ''), logid=suspect.id)

        message_uri = apply_template(self.config.get(self.section, 'message_uri_template'), suspect)
        sender_search_uri = apply_template(self.config.get(self.section, 'sender_search_uri_template'), suspect)
        server_search_uri = apply_template(self.config.get(self.section, 'server_search_uri_template'), suspect)

        body = f'Sender: {suspect.from_address}\n'
        body += f'Trap Recipient: {culprit}\n'
        body += f'Suspect ID: {suspect.id}\n'
        body += f'Subject: {subject}\n'
        body += f'Spam: {suspect.is_spam()}\n'
        body += f'Server info: {clientip} / {clienthostname} / {clienthelo}\n'
        if message_uri:
            body += f'Message: {message_uri}'
        if sender_search_uri:
            body += f'From: {sender_search_uri}'
        if server_search_uri:
            body += f'Server: {server_search_uri}'
        msg = suspect.wrap(reporter, reportto, subject, body, 'spam.eml', self.config)

        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info(f'{suspect.id} Spam report sent to {reporter} with queueid {queueid} for sender {suspect.from_address} and trap hit {suspect.to_address}')

    def _hash_mail(self, suspect):
        reportto = self.config.get(self.section, 'bounce_recipient')
        if not reportto:
            self.logger.info(f'{suspect.id} not reported because bounce recipient is not defined')
            return

        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'bounce_sender') or '<>'
        if reporter == '<>':
            reporter = ''

        # use buffer directly to prevent python EmailMessage conversion errors
        msg_buffer = suspect.get_original_source()
        # prepend header with original sender
        original_sender_header = self.config.get(self.section, 'original_sender_header')
        if original_sender_header:
            msg_buffer = Suspect.prepend_header_to_source(original_sender_header, suspect.from_address, msg_buffer)

        queueid = bounce.send(reporter, reportto, msg_buffer)
        self.logger.info(f'{suspect.id} Spam hashed with queueid {queueid}')


class KeepReject(ScannerPlugin):
    """
    This plugin will reject messages after EOD based on recipient domain.
    Use in combination with an AppenderPlugin such as Mailfeed to still fwd a copy.
    """
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars={
            'domains': {
                'default':'',
                'description':'comma separated list of recipient domains handled by this plugin',
            },
            
            'action': {
                'default': 'REJECT',
                'description': 'action if recipient is in domain list (DUNNO, REJECT, DELETE)',
            },
            
            'rejectmessage': {
                'default': 'message not accepted',
                'description': 'reject message template',
            },
            
            'acceptbounces': {
                'default': 'True',
                'description': 'set to True to accept bounces even if recipient domain would trigger other action',
            },
        }
    
    def examine(self,suspect):
        to_domain = suspect.to_domain
        if to_domain is None: # handle this case elsewhere...
            return DUNNO
        from_domain = suspect.from_domain
        if from_domain is None and self.config.getboolean(self.section, 'acceptbounces'):
            return DUNNO
        
        to_domain = to_domain.lower()
        domainlist = self.config.getlist(self.section, 'domains')
        
        if to_domain in domainlist:
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect)
            action = self.config.get(self.section, 'action')
            actioncode = string_to_actioncode(action, self.config)
            return actioncode, message
        else:
            return DUNNO

