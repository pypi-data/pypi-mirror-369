# -*- coding: utf-8 -*-
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

import smtplib
import logging
import socket
import tempfile
import os
import re
import time
import typing as tp

from fuglu.shared import Suspect, apply_template, get_outgoing_helo, fold_header
from fuglu.protocolbase import ProtocolHandler, BasicTCPServer
from fuglu.connectors.check import HealthCheckSuspect
from fuglu.stringencode import force_bString, force_uString
from fuglu.bounce import FugluSMTPClient


mailregex = re.compile(r"^[^@<>]{1,500}<((?:\".{0,500}\"|[^\"<>@\s]{1,500})@[^<>@\s]{1,500})>(\s.{0,500})?$",
                       flags=re.IGNORECASE)


def smtp_strip_address(address: str) -> tp.Tuple[tp.Optional[str], tp.Optional[str]]:
    """
    Parse MAIL FROM/ RCPT TO line, extract mail address and return remaining string as well
    if there is one.
    Args:
        address (str):
    Returns:
        str, str
    """

    # Regex should extract all valid mail addresses, and also invalid adresses
    # as long as they are not too misformatted
    try:
        firsthit = mailregex.search(address)
        if firsthit:
            return firsthit[1], firsthit[2].strip() if isinstance(firsthit[2], str) else firsthit[2]
    except Exception as e:
        logger = logging.getLogger("fuglu.smtp_strip_address")
        logger.warning(f"Error parsing line: {address} with regex, apply fallback method. error is {e.__class__.__name__}: {str(e)}")

    # Ending up here address is most probably not properly formatted.
    start = address.find('<') + 1
    if start < 1:
        start = address.find(':') + 1
    if start < 1:
        raise ValueError(f"Could not parse address {address}")

    # Ending up here, search from the left for the first closing bracket.
    # This avoids interference with additional optional parameters also using
    # brackets.
    end = address.find('>')
    if end < 0:
        end = len(address)
    retaddr = address[start:end]
    retaddr = retaddr.strip()

    remaining = ''
    if end + 1 < len(address):
        remaining = address[end + 1:]
        remaining = remaining.strip()
    return retaddr, remaining


def buildmsgsource(suspect):
    """Build the message source with fuglu headers prepended"""

    # we must prepend headers manually as we can't set a header order in email
    # objects

    # -> the original message source is bytes
    origmsgtxt = suspect.get_source()
    newheaders = ""

    for key in suspect.addheaders:
        val = suspect.addheaders[key]
        hdr = fold_header(key, val)
        newheaders += hdr

    # the original message should be in bytes, make sure the header added
    # is an encoded string as well
    modifiedtext = force_bString(newheaders) + force_bString(origmsgtxt)
    return modifiedtext


class SMTPHandler(ProtocolHandler):
    protoname = 'SMTP (after queue)'

    def __init__(self, sock, config):
        super().__init__(sock, config)
        self.sess = SMTPSession(sock, config)

    def re_inject(self, suspect):
        """Send message back to postfix"""
        if suspect.get_tag('noreinject'):
            return 250, 'message not re-injected by plugin request', '<>'

        if suspect.get_tag('reinjectoriginal'):
            self.logger.info(f'{suspect.id}: Injecting original message source without modifications')
            msgcontent = suspect.get_original_source()
        else:
            msgcontent = buildmsgsource(suspect)

        targethost: str = self.config.get('main', 'outgoinghost')
        if targethost == '${injecthost}':
            targethost = self.socket.getpeername()[0]
        elif targethost.startswith("$"):
            # extract target host from environment variable
            env_targethost = os.environ[targethost[1:]]
            if not env_targethost:
                raise ValueError(f"Could not extract outgoing host from environment var '{targethost}'")
            targethost = env_targethost

        outgoingport = self.config.getint('main', 'outgoingport')
        self.logger.info(f"{suspect.id} reinject message with size: {len(msgcontent)} to {targethost}:{outgoingport}")

        try:
            client = FugluSMTPClient(targethost, outgoingport)
        except Exception as e:
            self.logger.error(f'{suspect.id} failed to connect to {targethost}:{outgoingport} due to {e.__class__.__name__}: {str(e)}')
            raise
        helostring = get_outgoing_helo(self.config)

        # if there are SMTP options (SMTPUTF8, ...) then use ehlo
        mail_options = list(suspect.smtp_options)

        if "SMTPUTF8" not in mail_options:
            # make sure SMTPUTF8 option is set if there are addresses not purely ascii
            add_option = False
            if suspect.from_address:
                try:
                    force_uString(suspect.from_address).encode(encoding="ascii", errors="strict")
                except UnicodeEncodeError:
                    self.logger.warning(f'{suspect.id} reinject: trying to send from {suspect.from_address} without SMTPUTF8 option enabled')
                    add_option = True
            for rcpt in suspect.to_address:
                if rcpt:
                    try:
                        force_uString(rcpt).encode(encoding="ascii", errors="strict")
                    except UnicodeEncodeError:
                        self.logger.warning(f'{suspect.id} reinject: trying to send to {rcpt} without SMTPUTF8 option enabled')
                        add_option = True
            if add_option:
                mail_options.append("SMTPUTF8")
                self.logger.warning(f'{suspect.id} reinject: enable SMTPUTF8 option!')

        serveranswer = None
        responsecode = None
        queueid = None
        try:
            if mail_options:
                client.ehlo(helostring)
            else:
                client.helo(helostring)

            # for sending, make sure the string to sent is byte string
            client.sendmail(force_uString(suspect.from_address),
                            force_uString(suspect.recipients),
                            force_bString(msgcontent),
                            mail_options=mail_options)
            # if we did not get an exception so far, we can grab the server answer using the patched client
            # servercode=client.lastservercode
            responsecode = 250
            serveranswer = client.lastserveranswer
            queueid = client.queueid
        except (smtplib.SMTPHeloError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as e:
            if isinstance(e, smtplib.SMTPResponseException):
                responsecode = e.smtp_code
                serveranswer = e.smtp_error
            else:
                responsecode = 451
                serveranswer = str(e)
        finally:
            try:
                client.quit()
            except Exception as e:
                self.logger.warning(f'{suspect.id} Exception while quitting reinject session to {targethost}: {e.__class__.__name__}: {str(e)}')

        if responsecode is None:
            self.logger.warning(f'{suspect.id} reinject: could not get server response code from {targethost}')
            responsecode = 451
        if serveranswer is None:
            self.logger.warning(f'{suspect.id} reinject: could not get server answer from {targethost}')
            serveranswer = ''
        
        self.logger.debug(f'{suspect.id} reinjected message from={force_uString(suspect.from_address)} to={force_uString(suspect.recipients)} in={targethost} with queueid={queueid} code={responsecode} message={force_uString(serveranswer)}')
        # make sure serveranswer is unicode (could be bytes, error, ...)
        return responsecode, force_uString(serveranswer), queueid

    def get_suspect(self, **kwargs):
        success = self.sess.getincomingmail()
        if not success and not self.sess.healthcheck:
            self.logger.warning('incoming smtp transfer did not finish')
            return None

        sess = self.sess
        fromaddr = sess.from_address
        tempfilename = sess.tempfilename
        mfsize = sess.mfsize

        # Select a Suspect class
        SuspectClass = HealthCheckSuspect if sess.healthcheck else Suspect

        try:
            suspect = SuspectClass(fromaddr, sess.recipients, tempfilename,
                                   att_cachelimit=self._att_mgr_cachesize, smtp_options=sess.smtpoptions,
                                   att_defaultlimit=self._att_defaultlimit, att_maxlimit=self._att_maxlimit,
                                   mfsize=mfsize)
        except ValueError as e:
            if len(sess.recipients) > 0:
                toaddr = sess.recipients[0]
            else:
                toaddr = ''
            self.logger.error(f'failed to initialise suspect with from=<{fromaddr}> to=<{toaddr}> : {str(e)}')
            raise
        return suspect

    def commitback(self, suspect):
        retries = self.config.getint('main', 'outgoingretry', fallback=1)
        while retries>0:
            try:
                self._commitback(suspect)
                break
            except ConnectionError as e:
                retries=retries-1
                if retries == 0:
                    raise
                else:
                    self.logger.warning(f'{suspect.id} {e.__class__.__name__} in commitback: {str(e)}')
                    time.sleep(0.1)
            
    
    def _commitback(self, suspect):
        injectcode, injectanswer, queueid = self.re_inject(suspect)
        suspect.set_tag("injectanswer", injectanswer)
        suspect.set_tag("injectqueueid", queueid)

        if injectcode == 250:
            values = dict(injectanswer=injectanswer)
            message = apply_template(
                self.config.get('smtpconnector', 'requeuetemplate'), suspect, values)
        else:
            message = injectanswer

        self.sess.endsession(injectcode, message)
        self.sess = None

    def defer(self, reason):
        self.sess.endsession(451, reason)

    def discard(self, reason):
        self.sess.endsession(250, reason)

    def reject(self, reason):
        self.sess.endsession(550, reason)

    def healthcheck_reply(self):
        self.sess.endsession(250, "healthcheck")


class SMTPServer(BasicTCPServer):

    def __init__(self, controller, port=10125, address="127.0.0.1"):
        super().__init__(controller, port, address, SMTPHandler)


class SMTPSession(object):
    ST_INIT = 0
    ST_HELO = 1
    ST_MAIL = 2
    ST_RCPT = 3
    ST_DATA = 4
    ST_QUIT = 5

    def __init__(self, sock, config):
        self.config = config
        self.from_address = None
        self.recipients = []
        self.helo = None
        self.dataAccum = None

        self.socket = sock
        self.state = SMTPSession.ST_INIT
        self.logger = logging.getLogger("fuglu.smtpsession")
        self.tempfilename = None
        self.tempfile = None
        self.smtpoptions = set()
        self.ehlo_options = ["SMTPUTF8", "8BITMIME", "SIZE"]
        self.healthcheck = False
        # size optionally sent in MAIL FROM command
        self.mfsize = None

    def endsession(self, code, message):
        self.socket.send(force_bString(f'{code} {message}\r\n'))

        rawdata = b''
        while True:
            lump = self.socket.recv(1024)

            if len(lump):

                rawdata += lump
                if (len(rawdata) >= 2) and rawdata[-2:] == b'\r\n':
                    cmd = rawdata[0:4]
                    cmd = cmd.upper()
                    if cmd == b"QUIT":
                        self.socket.send(b"220 BYE\r\n")
                        self.closeconn()
                        return

                    self.socket.send(b"421 Cannot accept further commandsr\r\n")
                    self.closeconn()
                    return
            else:
                self.closeconn()
                return

    def closeconn(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except (OSError, socket.error):
            pass
        finally:
            self.socket.close()

    def _close_tempfile(self):
        if self.tempfile and not self.tempfile.closed:
            self.tempfile.close()

    def getincomingmail(self):
        """return true if mail got in, false on error Session will be kept open"""
        self.socket.send(b"220 fuglu scanner ready \r\n")

        while True:
            completeLine = 0
            collect_lumps = []
            while not completeLine:

                lump = self.socket.recv(1024)

                if len(lump):
                    # collect the lumps into a list
                    collect_lumps.append(lump)

                    # check for \r\n in the last two characters sent...
                    if len(lump) > 1:
                        if lump[-2:] == b'\r\n':
                            completeLine = 1
                    elif len(collect_lumps) > 1 and (lump[-1:] == b'\n' and collect_lumps[-2][-1:] == b'\r'):
                        # we reach here if the \r\n has been split:
                        # collect_lumps[-2] = b"....\r"
                        # lump = b"\n"
                        #
                        # Note the "-2" in collect_lumps because the current lump has been added already
                        completeLine = 1

                    if completeLine == 1:

                        # if line is complete, concatenate the bytes string
                        # this is MUCH FASTER than doing something like
                        # rawdata += lump
                        # outside the completeLine if-condition for every lump
                        rawdata = b"".join(collect_lumps)

                        if self.state != SMTPSession.ST_DATA:

                            # convert data to unicode if needed
                            data = force_uString(rawdata)
                            rsp, keep = self.doCommand(data)
                            if self.healthcheck:
                                return False

                        else:
                            try:
                                # directly use raw bytes-string data
                                rsp = self.doData(rawdata)
                            except IOError:
                                self.endsession(421, "Could not write to temp file")
                                self._close_tempfile()
                                return False

                            if rsp is None:
                                continue
                            else:
                                # data finished. keep connection open though
                                return True

                        self.socket.send(force_bString(rsp + "\r\n"))

                        if keep == 0:
                            self.closeconn()
                            return False
                else:
                    # EOF
                    self.logger.warning("EOF, something went wrong!")
                    return False

    def doCommand(self, data):
        """Process a single SMTP Command"""
        cmd = data[0:4]
        cmd = cmd.upper()
        keep = 1
        rv = "250 OK"
        if cmd == "HELO":
            self.state = SMTPSession.ST_HELO
            self.helo = data
            self.ehlo_options = []
        elif cmd == 'EHLO':
            self.state = SMTPSession.ST_HELO
            self.helo = data
            helo = get_outgoing_helo(self.config)
            if len(self.ehlo_options) > 0:
                answer = [helo] + self.ehlo_options
                rv = "250-"+"250-".join(a+"\n" for a in answer[:-1])+"250 "+answer[-1]
            else:
                rv = f'250 {helo}'
        elif cmd == "RSET":
            self.from_address = None
            self.recipients = []
            self.helo = None
            self.dataAccum = ""
            self.state = SMTPSession.ST_INIT
        elif cmd == "NOOP":
            pass
        elif cmd == "QUIT":
            keep = 0
        elif cmd == "HCHK":
            keep = 0
            self.healthcheck = True
        elif cmd == "MAIL":
            if self.state != SMTPSession.ST_HELO:
                return "503 Bad command sequence", 1
            self.state = SMTPSession.ST_MAIL
            self.from_address = self.stripAddress(data)
        elif cmd == "RCPT":
            if (self.state != SMTPSession.ST_MAIL) and (self.state != SMTPSession.ST_RCPT):
                return "503 Bad command sequence", 1
            self.state = SMTPSession.ST_RCPT
            rec = self.stripAddress(data)
            self.recipients.append(rec)
        elif cmd == "DATA":
            if self.state != SMTPSession.ST_RCPT:
                return "503 Bad command sequence", 1
            self.state = SMTPSession.ST_DATA
            self.dataAccum = b""
            try:
                (handle, tempfilename) = tempfile.mkstemp(prefix='fuglu', dir=self.config.get('main', 'tempdir'))
                self.tempfilename = tempfilename
                self.tempfile = os.fdopen(handle, 'w+b')
            except Exception as e:
                self.logger.error(f"could not create temp file in {self.config.get('main', 'tempdir')} due to {e.__class__.__name__}: {str(e)}")
                self.endsession(421, "Queue file write error")
                self._close_tempfile()
            return "354 OK, Enter data, terminated with a \\r\\n.\\r\\n", 1
        else:
            return "505 Bad SMTP command", 1

        return rv, keep

    def doData(self, data):
        """Store data in temporary file

        Args:
            data (str or bytes): data as byte-string

        """
        # store the last few bytes in memory to keep track when the msg is
        # finished
        self.dataAccum = self.dataAccum + data

        if len(self.dataAccum) > 4:
            self.dataAccum = self.dataAccum[-5:]

        # unquote data here after storing in dataAccum (which is used to detect end of message)
        data = self.unquoteData(data)

        if len(self.dataAccum) > 4 and self.dataAccum[-5:] == b'\r\n.\r\n':
            # check if there is more data to write to the file
            if len(data) > 4:
                self.tempfile.write(data[0:-5])

            self._close_tempfile()

            self.state = SMTPSession.ST_HELO
            return "250 OK - Data and terminator. found"
        else:
            self.tempfile.write(data)
            return None

    _re_dots = re.compile(rb'(?m)^\.\.')

    def unquoteData(self, data):
        """two leading dots at the beginning of a line must be unquoted to a single dot"""
        return self._re_dots.sub(b'.', force_bString(data))

    def stripAddress(self, address):
        """
        Strip the leading & trailing <> from an address.  Handy for
        getting FROM: addresses.
        """
        address = force_uString(address)
        retaddr, remaining = smtp_strip_address(address)

        if remaining:
            remaining = remaining.upper()
            self.logger.debug(f"stripAddress has remaining part, addr: {retaddr}, remaining: {remaining}")
            if "SMTPUTF8" in remaining:
                self.logger.debug("Address requires SMTPUTF8 support")
                if "SMTPUTF8" not in self.ehlo_options:
                    raise ValueError("SMTPUTF8 support was not proposed")
                self.smtpoptions.add("SMTPUTF8")

            if "8BITMIME" in remaining:
                if "8BITMIME" not in self.ehlo_options:
                    raise ValueError("8BITMIME support was not proposed")
                self.logger.debug("mail contains 8bit-MIME")
                self.smtpoptions.add("BODY=8BITMIME")

            if "SIZE=" in remaining:
                # try to extract mail size from MAIL FROM command
                try:
                    out = remaining.strip().split("SIZE=", 1)[1]
                    out = out.split()[0]
                    self.mfsize = int(out)
                except Exception as e:
                    self.logger.debug(f"Problem trying to extract size from {address}", exc_info=e)
                    pass
        return retaddr
