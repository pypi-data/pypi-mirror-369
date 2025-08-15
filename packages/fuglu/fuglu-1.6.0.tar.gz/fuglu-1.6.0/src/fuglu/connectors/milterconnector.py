# -*- coding: utf-8 -*-
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

import logging
import socket
import tempfile
import os
import time
import typing as tp
import copy

from typing import Tuple, Union
from io import BytesIO

from fuglu.protocolbase import ProtocolHandler, BasicTCPServer
from fuglu.stringencode import force_bString, force_uString
from fuglu.shared import Suspect, fold_header
from configparser import ConfigParser
from .asyncmilterconnector import MILTERMACROS, MILTERMACRO_TYPES

try:
    import libmilter as lm

    # overwrite debug logger if required
    # def debug(msg, level=1, protId=0):
    #     out = ''
    #     if protId:
    #         out += f'ID: {protId} ; '
    #     out += msg
    #     logging.getLogger("libmilter").debug(out)
    #lm.debug = debug

    LIMBMILTER_AVAILABLE = True

    ACCEPT = lm.ACCEPT
    CONTINUE = lm.CONTINUE
    REJECT = lm.REJECT
    TEMPFAIL = lm.TEMPFAIL
    DISCARD = lm.DISCARD
    CONN_FAIL = lm.CONN_FAIL
    SHUTDOWN = lm.SHUTDOWN
except ImportError:
    class lm:
        MilterProtocol = object
        SMFIF_ALLOPTS = None

        @staticmethod
        def noReply(self):
            pass

    LIMBMILTER_AVAILABLE = False
    ACCEPT = b"accept"
    CONTINUE = b"continue"
    REJECT = b"reject"
    TEMPFAIL = b"tempfail"
    DISCARD = b"discard"
    CONN_FAIL = b"conn_fail"
    SHUTDOWN = b"shutdown"


# string to return code
STR2RETCODE = {
    "accept": ACCEPT,
    "continue": CONTINUE,
    "reject": REJECT,
    "tempfail": TEMPFAIL,
    "discard": DISCARD,
    "conn_fail": CONN_FAIL,
    "shutdown": SHUTDOWN
}


RETCODE2STR = dict([(v, k) for k, v in STR2RETCODE.items()])


# states
CONNECT = "connect"
HELO = "helo"
MAILFROM = "mailfrom"
RCPT = "rcpt"
HEADER = "header"
EOH = "eoh"
EOB = "eob"


class MilterHandler(ProtocolHandler):
    protoname = 'MILTER V6'

    def __init__(self, sock, config):
        super().__init__(sock, config)
        self.logger = logging.getLogger(f'fuglu.{self.__class__.__name__}.sync')
        self.loggerheaders = logging.getLogger(f'fuglu.{self.__class__.__name__}.miltersession.headers')

        # Milter can keep the connection and handle several suspect in one session
        self.keep_connection = True

        if not LIMBMILTER_AVAILABLE:
            raise ImportError("libmilter not available, not possible to use MilterHandler")

        try:
            configstring = config.get('milter', 'milter_mode')
        except Exception:
            configstring = "tags"

        configstring = configstring.lower()

        if not configstring:
            self.logger.debug("milter_mode: setting to default value: 'tags'")
            configstring = "tags"

        if configstring not in ["auto", "readonly", "tags", "replace_demo", "manual", "autoheaders"]:
            self.logger.warning("milter_mode: '%s' not recognised, resetting to 'tags'" % configstring)

        self.enable_mode_manual = ("manual" == configstring)
        self.enable_mode_auto = ("auto" == configstring)
        self.enable_mode_autoheaders = ("autoheaders" == configstring)
        self.enable_mode_readonly = ("readonly" == configstring)
        self.enable_mode_tags = ("tags" == configstring)
        self.replace_demo = ("replace_demo" == configstring)

        sess_options = 0x00 if self.enable_mode_readonly else lm.SMFIF_ALLOPTS
        self.sess = MilterSession(sock, config, options=sess_options)

        self.logger.debug("Milter mode: auto=%s, readonly=%s, tags=%s, autoheaders=%s" %
                          (self.enable_mode_auto, self.enable_mode_readonly, self.enable_mode_tags,
                           self.enable_mode_autoheaders))

        # options (can be combined into a string): "all" "body" "headers" "from" "to"
        try:
            self.milter_mode_options = config.getlist('milter', 'milter_mode_options', lower=True)
        except Exception:
            self.milter_mode_options = []

        self.logger.debug("Milter config fixed replacements: all=%s, body=%s, headers=%s, from=%s, to=%s" %
                          ("all" in self.milter_mode_options, "body" in self.milter_mode_options,
                           "headers" in self.milter_mode_options, "from" in self.milter_mode_options,
                           "to" in self.milter_mode_options))

    def get_suspect(self, **kwargs):

        if 'milterplugins' in kwargs:
            milterplugins = kwargs.pop('milterplugins')
        else:
            milterplugins = {}

        # already generate Suspect id
        sessid = Suspect.generate_id()
        # set in session already for logging,
        # so we can link milter logs in different states to final suspect
        self.sess.id = sessid
        # set milter plugins dictionary
        self.sess.milterplugins = milterplugins

        if not self.sess.getincomingmail():
            self.logger.error(f'{sessid} MILTER SESSION NOT COMPLETED')
            return None
        self.logger.debug(f"{sessid} After getting incoming mail...")

        sess = self.sess
        from_address = force_uString(sess.get_cleaned_from_address())
        recipients = force_uString(sess.get_cleaned_recipients())

        # If there's no file
        temp_filename = sess.tempfilename
        if not temp_filename:
            return None

        # If there is a filename but no file
        if temp_filename and not os.path.exists(temp_filename):
            self.logger.warning(f"{sessid} File '{temp_filename}' not found for suspect creation! from: {from_address}, to: {recipients}")
            return None

        suspect = Suspect(from_address, recipients, temp_filename, att_cachelimit=self._att_mgr_cachesize,
                          att_defaultlimit=self._att_defaultlimit, att_maxlimit=self._att_maxlimit,
                          queue_id=sess.queueid, id=sessid, milter_macros=sess.milter_macros)
        suspect.timestamp = sess.timestamp

        # add headers
        for hdrname, hdrval in self.sess.addheaders.items():
            immediate = hdrname in self.sess._addheaders_immediate
            suspect.add_header(key=hdrname, value=hdrval, immediate=immediate)

        # add session tags to Suspect
        if self.sess.tags:
            suspect.tags.update(self.sess.tags)

        logging.getLogger('fuglu.MilterHandler.queueid').info(f'"{sessid}" "{sess.queueid if sess.queueid else "NOQUEUE"}"')

        if sess.heloname is not None and sess.addr is not None and sess.fcrdns is not None:
            suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.fcrdns)

        return suspect

    def replacebody(self, newbody):
        """
        Replace message body sending corresponding command to MTA
        using protocol stored in self.sess

        Args:
            newbody (string(encoded)): new message body
        """
        # check if option is available
        if not self.sess.has_option(lm.SMFIF_CHGBODY):
            self.logger.error(f'{self.sess.id} Change body called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.sess.has_option(lm.SMFIF_CHGBODY, client="fuglu"),
                               self.sess.has_option(lm.SMFIF_CHGBODY, client="mta")))
            return
        self.sess.replBody(force_bString(newbody))

    def addheader(self, key, value):
        """
        Add header in message sending corresponding command to MTA
        using protocol stored in self.sess

        Args:
            key (string(encoded)): header key
            value (string(encoded)): header value
        """
        if not self.sess.has_option(lm.SMFIF_ADDHDRS):
            self.logger.error(f'{self.sess.id} Add header called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.sess.has_option(lm.SMFIF_ADDHDRS, client="fuglu"),
                               self.sess.has_option(lm.SMFIF_ADDHDRS, client="mta")))
            return
        self.sess.addHeader(force_bString(key), force_bString(value))

    def changeheader(self, key, value):
        """
        Change header in message sending corresponding command to MTA
        using protocol stored in self.sess

        Args:
            key (string(encoded)): header key
            value (string(encoded)): header value
        """
        if not self.sess.has_option(lm.SMFIF_CHGHDRS):
            self.logger.error(f'{self.sess.id} Change header called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.sess.has_option(lm.SMFIF_CHGHDRS, client="fuglu"),
                               self.sess.has_option(lm.SMFIF_CHGHDRS, client="mta")))
            return
        self.sess.chgHeader(force_bString(key), force_bString(value))

    def change_from(self, from_address):
        """
        Change envelope from mail address.
        Args:
            from_address (unicode,str): new from mail address
        """
        if not self.sess.has_option(lm.SMFIF_CHGFROM):
            self.logger.error(f'{self.sess.id} Change from called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.sess.has_option(lm.SMFIF_CHGFROM, client="fuglu"),
                               self.sess.has_option(lm.SMFIF_CHGFROM, client="mta")))
            return
        self.sess.chgFrom(force_bString(from_address))

    def add_rcpt(self, rcpt):
        """
        Add a new envelope recipient
        Args:
            rcpt (str, unicode): new recipient mail address, with <> qualification
        """
        if not self.sess.has_option(lm.SMFIF_ADDRCPT_PAR):
            self.logger.error(f'{self.sess.id} Add rcpt called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.sess.has_option(lm.SMFIF_ADDRCPT_PAR, client="fuglu"),
                               self.sess.has_option(lm.SMFIF_ADDRCPT_PAR, client="mta")))
            return
        self.sess.addRcpt(force_bString(rcpt))

    def endsession(self):
        """Close session"""
        try:
            self.sess.close()
        except Exception:
            pass
        self.sess = None

    def continuesession(self):
        """Close session"""
        try:
            self.sess._exit_incomingmail = False
        except Exception:
            pass

    def remove_recipients(self):
        """
        Remove all the original envelope recipients
        """
        # use the recipient data from the session because
        # it has to match exactly
        for recipient in self.sess.recipients:
            self.logger.debug(f"{self.sess.id} Remove env recipient: {force_uString(recipient)}")
            self.sess.delRcpt(recipient)
        self.sess.recipients = []

    def remove_headers(self):
        """
        Remove all original headers
        """
        for key, value in self.sess.original_headers:
            self.loggerheaders.debug(f"{self.sess.id} Remove header-> {force_uString(key)}: {force_uString(value)}")
            self.changeheader(key, b"")
        self.sess.original_headers = []

    def commitback(self, suspect):
        """
        Commit message. Modify message if requested.
        Args:
            suspect (fuglu.shared.Suspect): the suspect

        """
        if self.enable_mode_readonly:
            self.sess.send(lm.CONTINUE)
            self.continuesession()
            return

        if self.replace_demo:
            msg = suspect.get_message_rep()
            from_address = msg.get("From", "unknown")
            to_address = msg.get("To", "unknown")
            suspect.set_message_rep(MilterHandler.replacement_mail(from_address, to_address))
            self.logger.warning(f"{suspect.id} Replace message by dummy template...")
            self.enable_mode_tags = True
            suspect.set_tag('milter_replace', 'all')

        # --------------- #
        # modifications   #
        # --------------- #
        replace_headers = False
        replace_body = False
        replace_from = False
        replace_to = False

        # --
        # check for changes if automatic mode is enabled
        # --
        if self.enable_mode_auto:
            replace_headers = False
            replace_body = suspect.is_modified()
            replace_from = suspect.orig_from_address_changed()
            replace_to = suspect.orig_recipients_changed()
            self.logger.debug(f"{suspect.id} Mode auto -> replace headers:{replace_headers} body:{replace_body} from:{replace_from} to:{replace_to}")

        # --
        # apply milter options from config
        # --
        if self.enable_mode_manual and self.milter_mode_options:
            if "all" in self.milter_mode_options:
                replace_headers = True
                replace_body = True
                replace_from = True
                replace_to = True
            if "body" in self.milter_mode_options:
                replace_body = True
            if "headers" in self.milter_mode_options:
                replace_headers = True
            if "from" in self.milter_mode_options:
                replace_from = True
            if "to" in self.milter_mode_options:
                replace_to = True
            self.logger.debug(f"{suspect.id} Mode options -> replace headers:{replace_headers} body:{replace_body} from:{replace_from} to:{replace_to}")

        # --
        # apply milter options from tags (which can be set by plugins)
        # --

        if self.enable_mode_tags:
            milter_replace_tag = suspect.get_tag('milter_replace')
            if milter_replace_tag:
                milter_replace_tag = milter_replace_tag.lower()
                if "all" in milter_replace_tag:
                    replace_headers = True
                    replace_body = True
                    replace_from = True
                    replace_to = True
                if "body" in milter_replace_tag:
                    replace_body = True
                if "headers" in milter_replace_tag:
                    replace_headers = True
                if "from" in milter_replace_tag:
                    replace_from = True
                if "to" in milter_replace_tag:
                    replace_from = True
                self.logger.debug(f"{suspect.id} Mode tags -> replace headers:{replace_headers} body:{replace_body} from:{replace_from} to:{replace_to}")

        # ----------------------- #
        # replace data in message #
        # ----------------------- #
        if replace_from:
            self.logger.warning(f"{suspect.id} Set new envelope \"from address\": {suspect.from_address}")
            self.change_from(suspect.from_address)

        if replace_to:
            # remove original recipients
            self.remove_recipients()

            # add new recipients, use list in suspect
            self.logger.warning(f"{suspect.id} Reset to {len(suspect.recipients)} envelope recipient(s)")
            for recipient in suspect.recipients:
                self.add_rcpt(recipient)

        if (self.enable_mode_auto or self.enable_mode_autoheaders) and not replace_headers:
            lvl = logging.WARNING if len(suspect.modified_headers) > 0 else logging.INFO
            self.logger.log(lvl, f"{suspect.id} Modify {len(suspect.modified_headers)} headers according to modification track in suspect")
            for key, val in iter(suspect.modified_headers.items()):
                hdr = fold_header(key, val, value_only=True)
                self.changeheader(key, hdr.encode())

        if replace_headers:
            self.logger.warning(f"{suspect.id} Remove {len(self.sess.original_headers)} original headers ")
            self.remove_headers()

            msg = suspect.get_message_rep()
            self.logger.warning(f"{suspect.id} Add {len(msg)} headers from suspect mail")
            for key, val in iter(msg.items()):
                self.loggerheaders.debug(f"{suspect.id} Add header from msg-> {key}: {val}")
                hdr = fold_header(key, val, value_only=True)
                self.addheader(key, hdr.encode())
        # --
        # headers to add, same as for the other connectors
        # --
        lvl = logging.WARNING if len(suspect.addheaders) > 0 else logging.INFO
        self.logger.log(lvl, f"{suspect.id} Add {len(suspect.addheaders)} headers as defined in suspect")
        for key, val in iter(suspect.addheaders.items()):
            self.loggerheaders.debug(f"{suspect.id} Add suspect header-> {key}: {val}")
            hdr = fold_header(key, val, value_only=True)
            self.addheader(key, hdr.encode())

        if replace_body:
            self.logger.warning(f"{suspect.id} Replace message body")
            msg_string = suspect.get_message_rep().as_string()
            # just dump everything below the headers

            newbody = msg_string[msg_string.find("\n\n")+len("\n\n"):]
            self.logger.info(f"{suspect.id} Replace with new body of size: {len(newbody)}")
            self.replacebody(newbody)

        self.sess.send(lm.CONTINUE)
        self.continuesession()

    @staticmethod
    def replacement_mail(from_address, to_address):
        """
        Create a mail replacing the whole original mail. This
        is for testing purposes...

        Args:
            from_address (str): New address for 'From' header
            to_address (str):  New address for 'To' header

        Returns:
            email: Python email representation

        """
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Replacement message info"
        msg['From'] = from_address
        msg['To'] = to_address

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nBad luck, your message has been replaced completely :-("
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               Bad luck!<br>
               Your message has been replaced completely &#9785
            </p>
          </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html', _charset="UTF-8")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        return msg

    def defer(self, reason):
        """
        Defer mail.
        Args:
            reason (str,unicode): Defer message
        """
        self.sess.set_reply_message(450, "", reason)

        self.logger.debug(f"{self.sess.id} defer message, reason: {reason}")
        self.continuesession()

    def reject(self, reason):
        """
        Reject mail.
        Args:
            reason (str,unicode): Reject message
        """
        self.sess.set_reply_message(550, "", reason)
        self.logger.debug(f"{self.sess.id} reject message, reason: {reason}")
        self.continuesession()

    def discard(self, reason):
        """
        Discard mail.
        Args:
            reason (str,unicode): Defer message, only for internal logging
        """
        self.sess.send(lm.DISCARD)
        self.logger.debug(f"{self.sess.id} discard message, reason: {reason}")
        self.continuesession()


class MilterSession(lm.MilterProtocol):
    def __init__(self,
                 sock: tp.Optional[socket.socket],
                 config: tp.Optional[ConfigParser] = None,
                 options: bytes = lm.SMFIF_ALLOPTS
                 ):
        # enable options for version 2 protocol
        super().__init__(opts=options)
        self.timestamp = time.time()
        self.transport = sock
        try:
            self.tmpdir = config.get('main', 'tempdir')
        except Exception:
            self.tmpdir = "/tmp"

        self.logger = logging.getLogger('fuglu.miltersession.sync')

        self.logger.debug("Options negotiated:")
        for smfip_option, smfip_string in iter(lm.SMFIP_PROTOS.items()):
            self.logger.debug("* %s: %s" % (smfip_string, bool(smfip_option & self.protos)))

        # connection
        self.heloname = None
        self.addr = None
        self.fcrdns = None
        self.ptr = None
        self.milter_macros = {}

        self.recipients = []
        self.sender = None

        self._buffer = None
        self._tempfile = None
        self._exit_incomingmail = False
        self._tempfile = None
        self.tempfilename = None
        self.original_headers = []
        self.be_verbose = True
        # postfix queue id
        self.queueid = None
        # SASL authentication
        self.sasl_login = None
        self.sasl_sender = None
        self.sasl_method = None
        # unique id
        self.id = None
        # plugins
        self.milterplugins = {}
        self.addheaders = {}
        self._addheaders_immediate = set()
        # tags (will be passed to Suspect)
        self.tags = copy.deepcopy(Suspect._default_tags)

    @property
    def sasl_user(self):
        return self.sasl_login

    def add_plugin_skip(self, pluginname: str, tag: str = "skipmplugins"):
        """Add plugin to skiplist"""
        if tag in self.tags:
            # append if already present
            self.tags[tag] = f"{self.tags[tag]},{pluginname}"
        else:
            # set tag
            self.tags[tag] = pluginname

    def skip_plugin(self, plugin, tag: str = "skipmplugins") -> bool:
        """Check if plugin is in skiplist"""
        from fuglu.mshared import BasicMilterPlugin
        plugin: tp.Union[str, BasicMilterPlugin]

        res = False
        try:
            skipstring = self.tags.get(tag)
            if isinstance(plugin, str):
                pluginname = plugin
            else:
                pluginname = plugin.__class__.__name__
            res = skipstring and pluginname in Suspect.getlist_space_comma_separated(skipstring)
        except Exception:
            pass
        return res

    def add_header(self, key: str, value: str, immediate: bool = False):
        """ Headers to add to mail (if allowed) """
        self.addheaders[key] = value
        if immediate:
            self._addheaders_immediate.add(key)

    def get_templ_dict(self) -> tp.Dict[str, tp.Any]:
        templdict = {}
        if self.id is not None:
            templdict['id'] = force_uString(self.id)
        if self.heloname is not None:
            templdict['heloname'] = force_uString(self.heloname)
        if self.fcrdns is not None:
            templdict['fcrdns'] = force_uString(self.fcrdns)
        if self.ptr is not None:
            templdict['ptr'] = force_uString(self.ptr)
        if self.addr is not None:
            templdict['addr'] = force_uString(self.addr)
        if self.queueid is not None:
            templdict['queueid'] = force_uString(self.queueid)
        if self.sasl_login is not None:
            templdict['sasl_login'] = force_uString(self.sasl_login)
        if self.sasl_user is not None:  # same as sasl_login
            templdict['sasl_user'] = force_uString(self.sasl_user)
        if self.sasl_sender is not None:
            templdict['sasl_sender'] = force_uString(self.sasl_sender)
        if self.from_address:
            templdict['from_address'] = self.from_address
        if self.from_domain:
            templdict['from_domain'] = self.from_domain
        # latest recipient
        if self.to_address:
            templdict['to_address'] = self.to_address
        if self.to_domain:
            templdict['to_domain'] = self.to_domain
        if self.size is not None:
            templdict['size'] = force_uString(self.size)

        # put tags also in template dict with prefix "tag_" so it can be
        # used in reject messages
        if self.tags:
            for tkey, tval in self.tags.items():
                templdict[f'tag_{tkey}'] = f"{tval}"
                
        for item in self.milter_macros:
                templdict[item] = force_uString(self.milter_macros[item])
        return templdict

    def reset_connection(self):
        """Reset all variables except to prepare for a second mail through the same connection.
        keep helo (heloname), ip address (addr) and hostname (fcrdns)"""
        self.recipients = []
        self.original_headers = []
        self.tempfile = None
        self._buffer = None
        if self.tempfilename and os.path.exists(self.tempfilename):
            try:
                os.remove(self.tempfilename)
                self.logger.info(f"{self.id} Abort -> removed temp file: {self.tempfilename}")
            except OSError:
                self.logger.error(f"{self.id} Could not remove tmp file: {self.tempfilename}")
                pass
        self.tempfilename = None
        # postfix queue id
        self.queueid = None
        # SASL authentication
        self.sasl_login = None
        self.sasl_sender = None
        self.sasl_method = None
        self.addheaders = {}
        self.tags = copy.deepcopy(Suspect._default_tags)
        self.id = Suspect.generate_id()

    def _clean_address(self, address: tp.Optional[bytes]) -> tp.Optional[bytes]:
        address_cleaned = None
        # convert address to string
        if address is not None:
            addr_split = address.split(b'\0', maxsplit=1)
            address_cleaned = addr_split[0].strip(b'<>')
            address_cleaned_stripped = address_cleaned.strip()
            if address_cleaned != address_cleaned_stripped:
                self.logger.info(f"{self.id} Stripped unnecessary spaces from from/to-address(position=1): '{address_cleaned}' -> '{address_cleaned_stripped}'")
            address_cleaned = address_cleaned_stripped.rstrip(b'.')  # remove trailing .
            address_cleaned_stripped = address_cleaned.strip()
            if address_cleaned != address_cleaned_stripped:
                self.logger.info(f"{self.id} Stripped unnecessary spaces from from/to-address(position=2): '{address_cleaned}' -> '{address_cleaned_stripped}'")
                address_cleaned = address_cleaned_stripped
        return address_cleaned

    def get_cleaned_from_address(self) -> bytes:
        """Return from_address, without <> qualification or other MAIL FROM parameters"""
        # now already cleaned while setting
        return self.sender

    def get_cleaned_recipients(self) -> tp.List[bytes]:
        """Return recipient addresses, without <> qualification or other RCPT TO parameters"""
        # now already cleaned while setting
        return self.recipients

    @property
    def tempfile(self):
        if self._tempfile is None:
            (handle, tempfilename) = tempfile.mkstemp(
                prefix='fuglu', dir=self.tmpdir)
            self.tempfilename = tempfilename
            self._tempfile = os.fdopen(handle, 'w+b')
        return self._tempfile

    @tempfile.setter
    def tempfile(self, value):
        try:
            self._tempfile.close()
        except Exception:
            pass
        self._tempfile = value

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = BytesIO()
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        try:
            # dump buffer to file
            self.tempfile.write(self.buffer.getbuffer())
            self.logger.debug(f"{self.id} dumped {self.buffer.getbuffer().nbytes} bytes to file {self.tempfilename}")
        except Exception:
            pass
        self._buffer = value

    @property
    def size(self):
        try:
            return self._buffer.getbuffer().nbytes
        except Exception:
            return 0

    @staticmethod
    def extract_domain(address: str, lowercase=True):
        if not address or address.lower() == "postmaster":
            return None
        else:
            try:
                user, domain = address.rsplit('@', 1)
                if lowercase:
                    domain = domain.lower()
                return domain
            except Exception:
                raise ValueError(f"invalid email address: '{address}'")

    @property
    def from_address(self):
        return force_uString(self.sender)

    @property
    def from_domain(self):
        from_address = self.from_address
        if from_address is None:
            return None
        try:
            return MilterSession.extract_domain(from_address)
        except ValueError:
            return None

    @property
    def to_address(self):
        if self.recipients:
            rec = force_uString(self.recipients[-1])
            return rec
        else:
            return None

    @property
    def to_domain(self):
        rec = self.to_address
        if rec is None:
            return None
        try:
            return MilterSession.extract_domain(rec)
        except ValueError:
            return None

    def set_reply_message(self, rcode: int, xcode: str, msg: str):
        def_xcode = ""
        if int(rcode/100) == 5:
            def_xcode = "5.7.1"
        elif int(rcode/100) == 4:
            def_xcode = "4.7.1"

        if xcode:
            self.setReply(rcode, xcode, msg)
        elif def_xcode:
            if not msg.startswith(def_xcode[:2]):
                self.setReply(rcode, def_xcode, msg)
            else:
                split = msg.split(" ", 1)
                if len(split) == 2:
                    self.setReply(rcode, split[0], split[1])
                else:
                    self.setReply(rcode, "", msg)
        else:
            self.setReply(rcode, "", msg)

    def setReply(self, rcode: int, xcode: str, msg: str):
        # actually setReply needs all bytes
        return super(__class__, self).setReply(force_bString(rcode), force_bString(xcode), force_bString(msg))

    def handle_milter_plugin_reply(self, res: Union[bytes, Tuple[bytes, str]]):
        """Handle reply from plugin which might contain a message to set for the reply"""
        try:
            outres, message = res
            returncode = outres
            if outres == TEMPFAIL:
                self.set_reply_message(450, "", message)
                # Deferred which will not send anything back to the mta.
                # (set_reply_message already sent the response...)
                returncode = lm.Deferred()
            elif outres == REJECT:
                self.set_reply_message(550, "", message)
                # Deferred which will not send anything back to the mta.
                # (set_reply_message already sent the response...)
                returncode = lm.Deferred()
        except Exception:
            outres = res
            returncode = res
            message = ""
        return outres, message, returncode

    def has_option(self, smfif_option, client=None):
        """
        Checks if option is available. Fuglu or mail transfer agent can
        be checked also separately.

        Args:
            smfif_option (int): SMFIF_* option as defined in libmilter
            client (str,unicode,None): which client to check ("fuglu","mta" or both)

        Returns:
            (bool): True if available

        """
        option_fuglu = True if smfif_option & self._opts else False
        option_mta = True if smfif_option & self._mtaOpts else False
        if client == "fuglu":
            return option_fuglu
        elif client == "mta":
            return option_mta
        else:
            return option_fuglu and option_mta

    def getincomingmail(self):
        self._sockLock = lm.DummyLock()
        while True and not self._exit_incomingmail:
            buf = ''
            try:
                self.log("receive data from transport")
                buf = self.transport.recv(lm.MILTER_CHUNK_SIZE)
                self.log("after receive")
            except (AttributeError, socket.error, socket.timeout) as e:
                # Socket has been closed, error or timeout happened
                self.log(f"receive error: {e}, buffer is: {buf}")
            if not buf:
                self.log("buf is empty -> return")
                return True
            elif self.be_verbose:
                self.log(f"buf is non-empty: {buf}")
            try:
                self.dataReceived(buf)
            except Exception as e:
                self.logger.error(f'AN EXCEPTION OCCURED IN {self.id}: {e.__class__.__name__}: {str(e)}')
                self.logger.exception(e)
                self.log("Call connectionLost")
                self.connectionLost()
                self.log("fail -> return false")
                return False
        return self._exit_incomingmail

    def log(self, msg):
        # function will be used by libmilter as well for logging
        # this is only for development/debugging, that's why it has
        # to be enabled in the source code
        if self.be_verbose:
            self.logger.debug(msg)

    def store_info_from_dict(self, command_dict):
        """Extract and store additional info passed by dict"""
        if command_dict:
            for item in MILTERMACROS:
                if not force_uString(item) in self.milter_macros:
                    value = command_dict.get(item)
                    if value:
                        conv = MILTERMACRO_TYPES.get(item, force_uString)
                        try:
                            value = conv(value)
                        except (TypeError, ValueError):
                            value = None
                        self.milter_macros[force_uString(item)] = value
            
            if not self.queueid:
                queueid = command_dict.get(b'i', None)
                if queueid:
                    self.queueid = force_uString(queueid)

            if not self.sasl_login:
                sasl_login = command_dict.get(b'auth_authen', None)
                if sasl_login:
                    self.sasl_login = force_uString(sasl_login)

            if not self.sasl_sender:
                sasl_sender = command_dict.get(b'auth_author', None)
                if sasl_sender:
                    self.sasl_sender = force_uString(sasl_sender)

            if not self.sasl_method:
                sasl_method = command_dict.get(b'auth_type', None)
                if sasl_method:
                    self.sasl_method = force_uString(sasl_method)
            if not self.ptr:
                ptr = command_dict.get(b'_', None)
                if ptr:
                    try:
                        self.ptr = force_uString(ptr).split(maxsplit=1)[0]
                    except Exception:
                        pass

    @staticmethod
    def dict_unicode(command_dict):
        commanddictstring = ''
        if command_dict:
            for key, value in iter(command_dict.items()):
                commanddictstring += force_uString(key) + ": " + force_uString(value) + ", "
        return commanddictstring

    def connect(self, hostname, family, ip, port, command_dict):
        self.log('Connect from %s:%d (%s) with family: %s, dict: %s' % (ip, port,
                                                                        hostname, family, str(command_dict)))
        self.store_info_from_dict(command_dict)
        if family not in (b'4', b'6', b'U'):
            self.logger.warning(f'{self.id} Return temporary fail since family is: {force_uString(family)}')
            self.logger.warning(f'{self.id} command dict is: {MilterSession.dict_unicode(command_dict)}')
            return lm.TEMPFAIL
        elif family == b"U":
            # we handle unix socket, but print debug message since it's not tested well
            self.logger.debug(f'Handle unix socket connection')
        if hostname is None or force_uString(hostname) == f'[{force_uString(ip)}]':
            hostname = 'unknown'

        self.fcrdns = hostname
        self.addr = ip
        self.log(f'ip:{self.addr}, fcrdns:{self.fcrdns}, ptr:{self.ptr}')
        plugins = self.milterplugins.get(CONNECT, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {CONNECT}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_connect(sess=self, host=self.fcrdns, addr=self.addr)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {CONNECT}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode

        return lm.CONTINUE

    def helo(self, helo_name):
        self.log('HELO: %s' % helo_name)
        self.heloname = force_uString(helo_name)
        plugins = self.milterplugins.get(HELO, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {HELO}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_helo(sess=self, helo=self.heloname)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {HELO}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode
        return lm.CONTINUE

    def mailFrom(self, from_address, command_dict):
        # store exactly what was received
        self.log('FROM_ADDRESS: %s, dict: %s' % (from_address, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        from_address = self._clean_address(from_address)
        self.sender = from_address
        plugins = self.milterplugins.get(MAILFROM, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {MAILFROM}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_mailfrom(sess=self, sender=self.sender)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {MAILFROM}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode
        return lm.CONTINUE

    def rcpt(self, recipient, command_dict):
        # store exactly what was received
        self.log('RECIPIENT: %s, dict: %s' % (recipient, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        recipient = self._clean_address(recipient)
        plugins = self.milterplugins.get(RCPT, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {RCPT}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_rcpt(sess=self, recipient=recipient)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {RCPT}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode
        # add recipient here so in case of one recipient being rejected while others are accepted, the recipients
        # array contains all the accepted recipients...
        if recipient is not None:
            self.recipients.append(recipient)

        return lm.CONTINUE

    def header(self, key, val, command_dict):
        self.log('HEADER, KEY: %s, VAL: %s, dict: %s' % (key, val, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        self.buffer.write(key+b": "+val+b"\n")
        # backup original headers
        self.original_headers.append((key, val))
        plugins = self.milterplugins.get(HEADER, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {HEADER}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_header(sess=self, key=key, value=val)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {HEADER}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode

        return lm.CONTINUE

    def eoh(self, command_dict):
        self.log('EOH, dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)
        self.buffer.write(b"\n")
        plugins = self.milterplugins.get(EOH, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {EOH}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_eoh(sess=self)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {EOH}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                return retcode
        return lm.CONTINUE

    def data(self, command_dict):
        self.log('DATA, dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)
        return lm.CONTINUE

    @lm.noReply
    def body(self, chunk, command_dict):
        self.log('BODY chunk: %d, dict: %s' % (len(chunk), MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        self.buffer.write(chunk)
        return lm.CONTINUE

    def eob(self, command_dict):
        self.log('EOB dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)

        plugins = self.milterplugins.get(EOB, [])
        for plug in plugins:
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} {EOB}-Plugin {plug} -> skip on tag request")
                continue
            res = plug.examine_eob(sess=self)
            res, msg, retcode = self.handle_milter_plugin_reply(res)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {EOB}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,'unknown')}")
                return retcode

        try:
            # dump buffer to temp file
            self.buffer = None
            self.tempfile = None
        except Exception as e:
            self.logger.exception(e)
            pass

        # set true to end the loop in "incomingmail"
        self._exit_incomingmail = True
        # To prevent the library from ending the connection, return
        # Deferred which will not send anything back to the mta. Thi
        # has to be done outside (See commit function in handler).
        return lm.Deferred()

    def close(self):
        # close the socket
        self.log('Close')
        if self.transport:
            try:
                try:
                    self.transport.shutdown(socket.SHUT_RDWR)
                except (OSError, socket.error) as e:
                    self.logger.warning(f"{self.id} while socket shutdown: {str(e)}")
                    pass
                self.transport.close()
            except Exception as e:
                self.logger.error(f"{self.id} during close: {e.__class__.__name__}: {str(e)}")
                pass

        # close the tempfile
        try:
            # close buffer directly without dumping file
            self._buffer = None
            self.tempfile = None
        except Exception as e:
            self.logger.error(f"{self.id} closing tempfile: {e.__class__.__name__}: {str(e)}")
            pass

    def abort(self):
        self.logger.debug('Abort has been called')
        self.reset_connection()


class MilterServer(BasicTCPServer):

    def __init__(self, controller, port=10125, address="127.0.0.1"):
        super().__init__(controller, port, address, MilterHandler)
        if not LIMBMILTER_AVAILABLE:
            raise ImportError("libmilter not available, not possible to use MilterServer")
