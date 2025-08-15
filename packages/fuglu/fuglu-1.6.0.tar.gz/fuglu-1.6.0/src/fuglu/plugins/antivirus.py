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

"""
Plugins for proprietary antivirus solutions.
May be untested and/or deprecated.
"""


from fuglu.shared import AVScannerPlugin, DUNNO, string_to_actioncode, actioncode_to_string, Suspect, \
    FuConfigParser, FileList, _SuspectTemplate
from fuglu.stringencode import force_bString, force_uString
from fuglu.protocolbase import set_keepalive_linux
from fuglu.utils.version import get_main_version
from fuglu.lib.patchedemail import PatchedMessage
from fuglu.mailattach import Mailattachment_mgr, NoExtractInfo
from fuglu.extensions.sql import get_session, text
import socket
import struct
import re
import os
import sys
import time
import email

try:
    import ssdeep
    HAVE_SSDEEP = True
except ImportError:
    from unittest.mock import MagicMock
    ssdeep = MagicMock()
    HAVE_SSDEEP = False


# Regular Expressions defining some messages from the SSSP server.
SSSP_acceptsyntax = re.compile(rb"^ACC\s+(.{0,1024}?)\s{0,1024}$")
SSSP_optionsyntax = re.compile(rb"^(\w+):\s{0,1024}(.{0,1024}?)\s{0,1024}$")
SSSP_virussyntax = re.compile(rb"^VIRUS\s{1,1024}(\S{1,1024})\s{1,1024}(.{0,1024})")
SSSP_typesyntax = re.compile(rb"^TYPE\s{1,1024}(\w{1,1024})")
SSSP_donesyntax = re.compile(rb"^DONE\s{1,1024}(\w{1,1024})\s+(\w{1,1024})\s+(.{0,1024}?)\s{0,1024}$")
SSSP_eventsyntax = re.compile(rb"^([A-Z]{1,1024})\s{1,1024}(\w{1,1024})")
SSSP_tmpdirsyntax = re.compile(r"(/tmp/savid_tmp[^/]{1,1024}/)(.{1,1024})")


class SSSPPlugin(AVScannerPlugin):
    """ This plugin scans the suspect using the sophos SSSP protocol.

Prerequisites: Requires a running sophos daemon with dynamic interface (SAVDI)
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where the SSSP server runs',
            },

            'port': {
                'default': '4010',
                'description': "tcp port or path to unix socket",
            },

            'timeout': {
                'default': '30',
                'description': 'socket timeout',
            },

            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned. ",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },

            'enginename': {
                'default': '',
                'description': 'set custom engine name (defaults to %s)' % self.enginename,
            },
        }
        self.logger = self._logger()
        self.enginename = 'sophos'
        self._last_line = None

    def __str__(self):
        return "Sophos AV"

    def examine(self, suspect):
        if self._check_too_big(suspect):
            return DUNNO

        content = suspect.get_source()

        for i in range(0, self.config.getint(self.section, 'retries')):
            try:
                viruses = self.scan_stream(content)
                actioncode, message = self._virusreport(suspect, viruses)
                return actioncode, message
            except Exception as e:
                self.logger.warning("%s Error encountered while contacting SSSP server (try %s of %s): %s" % (
                    suspect.id, i + 1, self.config.getint(self.section, 'retries'), str(e)))
                time.sleep(0.05)  # give savdi a few ms before retrying
        self.logger.error("%s SSSP scan failed after %s retries" %
                          (suspect.id, self.config.getint(self.section, 'retries')))

        return self._problemcode()

    def scan_stream(self, content, suspectid='(NA)'):
        """
        Scan a buffer

        content (string) : buffer to scan

        return either :
          - (dict) : {filename1: "virusname"}
          - None if no virus found
        """

        s = self.__init_socket__()
        dr = {}

        # Read the welcome message

        if not self._exchange_greetings(s):
            raise Exception("SSSP Greeting failed: %s" % self._last_line)

        # QUERY to discover the maxclassificationsize
        s.send(b'SSSP/1.0 QUERY\n')

        if not self._accepted(s):
            raise Exception("SSSP Query rejected: %s" % self._last_line)

        self._read_options(s)

        # Set the options for classification
        enableoptions = [
            b"TnefAttachmentHandling",
            b"ActiveMimeHandling",
            b"Mime",
            b"ZipDecompression",
            b"DynamicDecompression",
        ]

        enablegroups = [
            b'GrpExecutable',
            b'GrpArchiveUnpack',
            b'GrpSelfExtract',
            b'GrpInternet',
            b'GrpSuper',
            b'GrpMisc',
        ]

        sendbuf = "OPTIONS\nreport:all\n"
        for opt in enableoptions:
            sendbuf += "savists: %s 1\n" % force_uString(opt)

        for grp in enablegroups:
            sendbuf += "savigrp: %s 1\n" % force_uString(grp)

        # all sent, add aditional newline
        sendbuf += "\n"

        s.send(force_bString(sendbuf))

        if not self._accepted(s):
            raise Exception("SSSP Options not accepted: %s" % self._last_line)

        resp = self._receive_msg(s)

        for l in resp:
            if SSSP_donesyntax.match(l):
                parts = SSSP_donesyntax.findall(l)
                if parts[0][0] != b'OK':
                    raise Exception("SSSP Options failed")
                break

        # Send the SCAN request

        s.send(force_bString('SCANDATA ' + str(len(content)) + '\n'))
        if not self._accepted(s):
            raise Exception("SSSP Scan rejected: %s" % self._last_line)

        s.sendall(force_bString(content))

        # and read the result
        events = self._receive_msg(s)

        for l in events:
            if SSSP_virussyntax.match(l):
                parts = SSSP_virussyntax.findall(l)
                virus = force_uString(parts[0][0])
                filename = force_uString(parts[0][1])
                try:
                    filename = SSSP_tmpdirsyntax.findall(filename)[0][1]
                except IndexError:
                    pass
                dr[filename] = virus

        try:
            self._say_goodbye(s)
            s.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            self.logger.warning('%s Error terminating connection: %s', (suspectid, str(e)))
        finally:
            s.close()

        if dr == {}:
            return None
        else:
            return dr

    def __init_socket__(self):
        unixsocket = False

        try:
            self.config.getint(self.section, 'port')
        except ValueError:
            unixsocket = True

        if unixsocket:
            sock = self.config.get(self.section, 'port')
            if not os.path.exists(sock):
                raise Exception("unix socket %s not found" % sock)
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(self.config.getfloat(self.section, 'timeout'))
            try:
                s.connect(sock)
            except socket.error:
                raise Exception('Could not reach SSSP server using unix socket %s' % sock)
        else:
            host = self.config.get(self.section, 'host', resolve_env=True)
            port = self.config.getint(self.section, 'port')
            timeout = self.config.getfloat(self.section, 'timeout')
            try:
                s = socket.create_connection((host, port), timeout)
            except socket.error:
                raise Exception('Could not reach SSSP server using network (%s, %s)' % (host, port))
            set_keepalive_linux(s)

        return s

    def _receive_line(self, s):
        """
        Receives a line of text from the socket
        \r chars are discarded
        The line is terminated by a \n
        NUL chars indicate a broken socket
        :param s: the socket
        :return: data read from socket
        """
        line = b''
        done = 0
        while not done:
            c = s.recv(1)
            if c == b'':
                return b''
            done = (c == b'\n')
            if not done and c != b'\r':
                line = line + c
        self._last_line = line
        return line

    def _receive_msg(self, s):
        """
        Receives a whole message. Messages are terminated by a blank line
        :param s: the socket
        :return: list of lines received
        """
        response = []
        finished = 0

        while not finished:
            msg = self._receive_line(s)
            finished = (len(msg) == 0)
            if not finished:
                response.append(msg)

        return response

    def _accepted(self, s):
        """
        Receives the ACC message which is a single line
        conforming to the acceptsyntax RE.
        :param s: the socket
        :return: boolean: does line start with ACC?
        """
        acc = self._receive_line(s)
        return SSSP_acceptsyntax.match(acc)

    def _read_options(self, s):
        """
        Reads a message which should be a list of options
        and transforms them into a dictionary
        :param s: the socket
        :return: dict: options supported by sophos
        """
        resp = self._receive_msg(s)
        opts = {}

        for l in resp:
            parts = SSSP_optionsyntax.findall(l)
            for p in parts:
                p0 = force_uString(p[0])
                if p0 not in opts:
                    opts[p0] = []

                opts[p0].append(force_uString(p[1]))

        return opts

    def _exchange_greetings(self, s):
        """
        Performs the initial exchange of messages.
        :param s: the socket
        :return: 1 on success, 0 if greeting failed
        """
        line = self._receive_line(s)

        if not line.startswith(b'OK SSSP/1.0'):
            return 0

        s.send(b'SSSP/1.0\n')

        if not self._accepted(s):
            print("Greeting Rejected!!")
            return 0

        return 1

    def _say_goodbye(self, s):
        """
        performs the final exchange of messages
        :param s: the socket
        :return: None
        """
        s.send(b'BYE\n')
        self._receive_line(s)

    def lint(self):
        viract = self.config.get(self.section, 'virusaction')
        print("Virusaction: %s" % actioncode_to_string(string_to_actioncode(viract, self.config)))
        allok = self.check_config() and self.lint_eicar()
        return allok


# from : https://github.com/AlexeyDemidov/avsmtpd/blob/master/drweb.h
# Dr. Web daemon commands
DRWEBD_SCAN_CMD = 0x0001
DRWEBD_VERSION_CMD = 0x0002
DRWEBD_BASEINFO_CMD = 0x0003
DRWEBD_IDSTRING_CMD = 0x0004
# DRWEBD_SCAN_FILE command flags: */
DRWEBD_RETURN_VIRUSES = 0x0001
DRWEBD_RETURN_REPORT = 0x0002
DRWEBD_RETURN_CODES = 0x0004
DRWEBD_HEURISTIC_ON = 0x0008
DRWEBD_SPAM_FILTER = 0x0020
# DrWeb result codes */
DERR_READ_ERR = 0x00001
DERR_WRITE_ERR = 0x00002
DERR_NOMEMORY = 0x00004
DERR_CRC_ERROR = 0x00008
DERR_READSOCKET = 0x00010
DERR_KNOWN_VIRUS = 0x00020
DERR_UNKNOWN_VIRUS = 0x00040
DERR_VIRUS_MODIFICATION = 0x00080
DERR_TIMEOUT = 0x00200
DERR_SYMLINK = 0x00400
DERR_NO_REGFILE = 0x00800
DERR_SKIPPED = 0x01000
DERR_TOO_BIG = 0x02000
DERR_TOO_COMPRESSED = 0x04000
DERR_BAD_CAL = 0x08000
DERR_EVAL_VERSION = 0x10000
DERR_SPAM_MESSAGE = 0x20000
DERR_VIRUS = DERR_KNOWN_VIRUS | DERR_UNKNOWN_VIRUS | DERR_VIRUS_MODIFICATION


class DrWebPlugin(AVScannerPlugin):
    """ This plugin passes suspects to a DrWeb scan daemon

EXPERIMENTAL Plugin: has not been tested in production.

Prerequisites: Dr.Web unix version must be installed and running, not necessarily on the same box as fuglu though.

Notes for developers:

Tags:

 * sets ``virus['drweb']`` (boolean)
 * sets ``DrWebPlugin.virus`` (list of strings) - virus names found in message
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)

        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where fpscand runs',
            },
            'port': {
                'default': '3000',
                'description': "DrWeb daemon port",
            },
            'timeout': {
                'default': '30',
                'description': "network timeout",
            },
            'maxsize': {
                'default': '22000000',
                'description': "maximum message size to scan",
            },
            'retries': {
                'default': '3',
                'description': "maximum retries on failed connections",
            },
            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "plugin action if threat is detected",
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "plugin action if scan fails",
            },
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
            'enginename': {
                'default': '',
                'description': 'set custom engine name (defaults to %s)' % self.enginename,
            },
        }
        self.logger = self._logger()
        self.pattern = re.compile(r'(?:DATA\[\d{1,1024}\])(.{1,1024}) infected with (.{1,1024})$')
        self.enginename = 'drweb'

    def _parse_result(self, lines, suspectid):
        dr = {}
        for line in lines:
            line = line.strip()
            m = self.pattern.search(line)
            if m is None:
                continue
            filename = m.group(1)
            virus = m.group(2)
            dr[filename] = virus

        if len(dr) == 0:
            self.logger.warning("%s could not extract virus information from report: %s" % (suspectid, "\n".join(lines)))
            return dict(buffer='infection details unavailable')
        else:
            return dr

    def scan_stream(self, content, suspectid='(NA)'):
        """
        Scan a buffer

        content (string) : buffer to scan

        return either :
          - (dict) : {filename: "virusname"}
          - None if no virus found
        """

        s = self.__init_socket__()
        buflen = len(content)

        self._sendint(s, DRWEBD_SCAN_CMD)

        # flags:
        # self._sendint(s, 0) # "flags" # use this to get only the code
        # self._sendint(s, DRWEBD_RETURN_VIRUSES) # use this to get the virus
        # infection name
        # use this to get the full report
        self._sendint(s, DRWEBD_RETURN_REPORT)
        self._sendint(s, 0)  # not sure what this is for - but it's required.
        self._sendint(s, buflen)  # send the buffer length
        s.sendall(content)  # send the buffer
        retcode = self._readint(s)  # get return code
        # print "result=%s"%retcode
        numlines = self._readint(s)
        lines = []
        for _ in range(numlines):
            line = self._readstr(s)
            lines.append(line)
        s.close()

        if retcode & DERR_VIRUS == retcode:
            return self._parse_result(lines, suspectid)
        else:
            return None

    def __init_socket__(self):
        host = self.config.get(self.section, 'host', resolve_env=True)
        port = self.config.getint(self.section, 'port')
        timeout = self.config.getint(self.section, 'timeout')
        try:
            s = socket.create_connection((host, port), timeout)
        except socket.error:
            raise Exception('Could not reach drweb using network (%s, %s)' % (host, port))

        return s

    def __str__(self):
        return 'DrWeb AV'

    def lint(self):
        allok = self.check_config() and self.lint_info() and self.lint_eicar()
        return allok

    def lint_info(self):
        try:
            version = self.get_version()
            bases = self.get_baseinfo()
            print("DrWeb Version %s, found %s bases with a total of %s virus definitions" % (
                version, len(bases), sum([x[1] for x in bases])))
        except Exception as e:
            print("Could not get DrWeb Version info: %s" % str(e))
            return False
        return True

    def get_version(self):
        """Return numeric version of the DrWeb daemon"""
        try:
            s = self.__init_socket__()
            self._sendint(s, DRWEBD_VERSION_CMD)
            version = self._readint(s)
            return version
        except Exception as e:
            self.logger.error("Could not get DrWeb Version: %s" % str(e))
        return None

    def get_baseinfo(self):
        """return list of tuples (basename,number of virus definitions)"""
        ret = []
        try:
            s = self.__init_socket__()
            self._sendint(s, DRWEBD_BASEINFO_CMD)
            numbases = self._readint(s)
            for _ in range(numbases):
                idstr = self._readstr(s)
                numviruses = self._readint(s)
                ret.append((idstr, numviruses))
        except Exception as e:
            self.logger.error(
                "Could not get DrWeb Base Information: %s" % str(e))
            return None
        return ret

    def _sendint(self, sock, value):
        sock.sendall(struct.pack('!I', value))

    def _readint(self, sock):
        res = sock.recv(4)
        ret = struct.unpack('!I', res)[0]
        return ret

    def _readstr(self, sock):
        strlength = self._readint(sock)
        buf = sock.recv(strlength)
        if buf[-1] == '\0':  # chomp null terminated string
            buf = buf[:-1]
        return buf


def drweb_main():
    import logging

    logging.basicConfig(level=logging.DEBUG)
    config = FuConfigParser()
    sec = 'dev'
    config.add_section(sec)
    config.set(sec, 'host', 'localhost')
    config.set(sec, 'port', '3000')
    config.set(sec, 'timeout', '5')
    plugin = DrWebPlugin(config, sec)

    assert plugin.lint_info()

    import sys

    if len(sys.argv) > 1:
        counter = 0
        infected = 0
        for file in sys.argv[1:]:
            counter += 1
            with open(file, 'rb') as fp:
                buf = fp.read()
            res = plugin.scan_stream(buf)
            if res is None:
                print("%s: clean" % file)
            else:
                infected += 1
                print("%s: infection(s) found: " % file)
                for fname, infection in res.items():
                    print("- %s is infected with %s" % (fname, infection))
        print("")
        print("%s / %s files infected" % (infected, counter))
    else:
        plugin.lint_eicar()


class ICAPPlugin(AVScannerPlugin):
    """ICAP Antivirus Plugin
This plugin allows Antivirus Scanning over the ICAP Protocol ( https://www.rfc-editor.org/rfc/rfc3507 )
supported by some AV Scanners like Symantec and Sophos. For sophos, however, it is recommended to use the native SSSP Protocol.

Prerequisites: requires an ICAP capable antivirus engine somewhere in your network
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where the ICAP server runs',
            },

            'port': {
                'default': '1344',
                'description': "tcp port or path to unix socket",
            },

            'timeout': {
                'default': '10',
                'description': 'socket timeout',
            },

            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned. ",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },

            'service': {
                'default': 'AVSCAN',
                'description': 'ICAP Av scan service, usually AVSCAN (sophos, symantec, eset)',
            },

            'send_fakeheaders': {
                'default': 'False',
                'description': 'send ICAP fake response headers (must be False for eset)',
            },

            'enginename': {
                'default': 'icap-generic',
                'description': "name of the virus engine behind the icap service. used to inform other plugins. can be anything like 'sophos', 'symantec', ...",
            },
        }
        self.logger = self._logger()
        self.enginename = 'icap-generic'

    def __str__(self):
        classname = self.__class__.__name__
        if self.section == classname:
            return "ICAP AV"
        else:
            return f'ICAP AV - {self.section}'

    def scan_stream(self, content, suspectid='(NA)'):
        """
        Scan a buffer

        content (string) : buffer to scan

        return either :
          - (dict) : {filename1: "virusname"}
          - None if no virus found
        """

        s = self.__init_socket__()
        dr = {}

        content = force_bString(content)
        CRLF = b"\r\n"
        host = self.config.get(self.section, 'host', resolve_env=True)
        port = self.config.get(self.section, 'port')
        service = self.config.get(self.section, 'service')
        send_fakeheaders = self.config.getboolean(self.section, 'send_fakeheaders')
        buflen = len(content)

        bodyparthexlen = hex(buflen)[2:].encode()
        bodypart = bodyparthexlen + CRLF
        bodypart += content + CRLF
        bodypart += b"0" + CRLF

        # now that we know the length of the fake request/response, we can
        # build the ICAP header
        icapheader = b""
        icapheader += b"RESPMOD icap://%s:%s/%s ICAP/1.0%s" % (host.encode(), port.encode(), service.encode(), CRLF)
        icapheader += b"Host: " + host.encode() + CRLF
        icapheader += b"User-Agent: Fuglu/%s%s" % (get_main_version().strip().encode(), CRLF)
        icapheader += b"Allow: 204" + CRLF
        
        if send_fakeheaders:
            fakerequestheader = b"GET http://localhost/message.eml HTTP/1.1%s" + CRLF
            fakerequestheader += b"Host: localhost" + CRLF
            fakerequestheader += CRLF
            fakereqlen = len(fakerequestheader)

            fakeresponseheader = b"HTTP/1.1 200 OK" + CRLF
            fakeresponseheader += b"Content-Length: " + str(buflen).encode() + CRLF
            fakeresponseheader += CRLF
            fakeresplen = len(fakeresponseheader)

            hdrstart = 0
            responsestart = fakereqlen
            bodystart = fakereqlen + fakeresplen
            icapheader += b"Encapsulated: req-hdr=%s, res-hdr=%s, res-body=%s%s" % (hdrstart, responsestart, bodystart, CRLF)
            everything = icapheader + CRLF + fakerequestheader + fakeresponseheader + bodypart + CRLF
        else:
            icapheader += b"Encapsulated: res-body=0" + CRLF
            everything = icapheader + CRLF + bodypart + CRLF
            
        #print(f"sending: {everything}")
        s.sendall(everything)
        result = force_uString(s.recv(20000))
        s.close()
        #print(f"result is: {result}")

        sheaders = ['X-Infection-Found', "X-Violations-Found:", ]
        for sheader in sheaders:
            if sheader.lower() in result.lower():
                lines = result.split('\n')
                lineidx = 0

                for line in lines:
                    if sheader.lower() in line.lower():
                        if sheader == 'X-Infection-Found':  # ESET
                            # X-Infection-Found: Type=0; Resolution=0; Threat=Eicar;
                            fields = [x.strip().split('=') for x in line.split(';')]
                            for field in fields:
                                if len(field) == 2 and field[0].lower() == 'threat':
                                    dr['stream'] = field[1]

                        if sheader == 'X-Violations-Found:':  # Sophos, Kaspersky?
                            numfound = int(line[len(sheader):])
                            # for each found virus, get 4 lines
                            for vircount in range(numfound):
                                infectedfile = lines[lineidx + vircount * 4 + 1].strip()
                                infection = lines[lineidx + vircount * 4 + 2].strip()
                                dr[infectedfile] = infection

                        break
                    lineidx += 1
                if dr:
                    break

        if dr == {}:
            return None
        else:
            return dr

    def lint_options(self):
        CRLF = "\r\n"
        host = self.config.get(self.section, 'host', resolve_env=True)
        port = self.config.get(self.section, 'port')
        service = self.config.get(self.section, 'service')

        icapheader = ''
        icapheader += "OPTIONS icap://%s:%s/%s ICAP/1.0%s" % (host, port, service, CRLF)
        icapheader += "Host: " + host + CRLF
        icapheader += "User-Agent: Fuglu/%s%s" % (get_main_version().strip(), CRLF)

        s = self.__init_socket__()
        s.sendall(force_bString(icapheader))
        result = s.recv(20000)
        s.close()
        print(force_uString(result))

    def lint(self):
        viract = self.config.get(self.section, 'virusaction')
        print("Virusaction: %s" % actioncode_to_string(string_to_actioncode(viract, self.config)))
        allok = self.check_config()
        # self.lint_options()
        allok = allok and self.lint_eicar()
        return allok


class FprotPlugin(AVScannerPlugin):
    """ This plugin passes suspects to an f-prot scan daemon

Prerequisites: f-protd must be installed and running, not necessarily on the same box as fuglu though.

Notes for developers:


Tags:

 * sets ``virus['F-Prot']`` (boolean)
 * sets ``FprotPlugin.virus`` (list of strings) - virus names found in message
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where fpscand runs',
            },
            'port': {
                'default': '10200',
                'description': "fpscand port",
            },
            'timeout': {
                'default': '30',
                'description': "network timeout",
            },
            'networkmode': {
                'default': 'False',
                'description': "Always send data over network instead of just passing the file name when possible. If fpscand runs on a different host than fuglu, you must enable this.",
            },
            'scanoptions': {
                'default': '',
                'description': 'additional scan options  (see `man fpscand` -> SCANNING OPTIONS for possible values)',
            },
            'maxsize': {
                'default': '10485000',
                'description': "maximum message size to scan",
            },
            'retries': {
                'default': '3',
                'description': "maximum retries on failed connections",
            },
            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "plugin action if threat is detected",
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "plugin action if scan fails",
            },
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
            'enginename': {
                'default': '',
                'description': 'set custom engine name (defaults to %s)' % self.enginename,
            },
        }

        self.pattern = re.compile(rb'^(\d){1,1024} <(.{1,1024})> (.{1,1024})$')
        self.enginename = 'F-Prot'

    def examine(self, suspect):
        if self._check_too_big(suspect):
            return DUNNO

        # use msgrep only to check for Content-Type header
        # use source directly for Fprot to prevent exceptions converting the email-object to bytes
        msgrep = suspect.get_message_rep()
        content = suspect.get_original_source()

        networkmode = self.config.getboolean(self.section, 'networkmode')

        # this seems to be a bug in f-prot.
        # If no Content-Type header is set, then no scan is performed.
        # However, content of the header does not seem to matter.
        # Therefore, we set a temporary dummy Content-Type header.
        if not 'Content-Type'.lower() in [k.lower() for k in msgrep.keys()]:
            content = Suspect.prepend_header_to_source('Content-Type', 'dummy', content)
            networkmode = True
            self.logger.debug('%s missing Content-Type header... falling back to network mode' % suspect.id)

        for i in range(0, self.config.getint(self.section, 'retries')):
            try:
                if networkmode:
                    viruses = self.scan_stream(content, suspect.id)
                else:
                    viruses = self.scan_file(suspect.tempfile, suspect.id)
                actioncode, message = self._virusreport(suspect, viruses)
                return actioncode, message
            except Exception as e:
                self.logger.warning("%s Error encountered while contacting fpscand (try %s of %s): %s" %
                                    (suspect.id, i + 1, self.config.getint(self.section, 'retries'), str(e)))
        self.logger.error("%s fpscand failed after %s retries" % (suspect.id, self.config.getint(self.section, 'retries')))

        return self._problemcode()

    def _parse_result(self, result, suspectid):
        dr = {}
        result = force_uString(result)
        for line in result.strip().split('\n'):
            m = self.pattern.match(force_bString(line))
            if m is None:
                self.logger.error('%s Could not parse line from f-prot: %s' % (suspectid, line))
                raise Exception('f-prot: Unparseable answer: %s' % result)
            status = force_uString(m.group(1))
            scantext = force_uString(m.group(2))
            details = force_uString(m.group(3))

            status = int(status)
            self.logger.debug("%s f-prot scan status: %s / scan text %s" % (suspectid, status, scantext))
            if status == 0:
                continue

            if status > 3:
                self.logger.warning("%s f-prot: got unusual status %s (result: %s)" % (suspectid, status, result))

            # http://www.f-prot.com/support/helpfiles/unix/appendix_c.html
            if status & 1 == 1 or status & 2 == 2:
                # we have an infection
                if scantext[0:10] == "infected: ":
                    scantext = scantext[10:]
                elif scantext[0:27] == "contains infected objects: ":
                    scantext = scantext[27:]
                else:
                    self.logger.warning("%s Unexpected reply from f-prot: %s" % (suspectid, scantext))
                    continue
                dr[details] = scantext

        if len(dr) == 0:
            return None
        else:
            return dr

    def scan_file(self, filename, suspectid):
        filename = os.path.abspath(filename)
        s = self.__init_socket__()
        s.sendall(force_bString('SCAN %s FILE %s' % (self.config.get(self.section, 'scanoptions'), filename)))
        s.sendall(b'\n')

        result = s.recv(20000)
        if len(result) < 1:
            self.logger.error(f'{suspectid} Got no reply from fpscand')
        s.close()

        return self._parse_result(result, suspectid)

    def scan_stream(self, content, suspectid='(NA)'):
        """
        Scan a buffer

        content (string) : buffer to scan

        return either :
          - (dict) : {filename1: "virusname"}
          - None if no virus found
        """

        s = self.__init_socket__()
        content = force_bString(content)
        buflen = len(content)
        s.sendall(force_bString('SCAN %s STREAM fu_stream SIZE %s' % (self.config.get(self.section, 'scanoptions'), buflen)))
        s.sendall(b'\n')
        self.logger.debug('%s Sending buffer (length=%s) to fpscand...' % (suspectid, buflen))
        s.sendall(content)
        self.logger.debug('%s Sent %s bytes to fpscand, waiting for scan result' % (suspectid, buflen))

        result = force_uString(s.recv(20000))
        if len(result) < 1:
            self.logger.error(f'{suspectid} Got no reply from fpscand')
        s.close()

        return self._parse_result(result, suspectid)

    def __init_socket__(self):
        host = self.config.get(self.section, 'host', resolve_env=True)
        port = self.config.getint(self.section, 'port')
        socktimeout = self.config.getint(self.section, 'timeout')
        try:
            s = socket.create_connection((host, port), socktimeout)
        except socket.error:
            raise Exception('Could not reach fpscand using network (%s, %s)' % (host, port))
        return s

    def __str__(self):
        return 'F-Prot AV'

    def lint(self):
        allok = self.check_config() and self.lint_eicar()
        networkmode = self.config.getboolean(self.section, 'networkmode')
        if not networkmode:
            allok = allok and self.lint_file()
        return allok

    def lint_file(self):
        import tempfile
        handle, tempfilename = tempfile.mkstemp(prefix='fuglu', dir=self.config.get('main', 'tempdir'))

        with os.fdopen(handle, 'w+b') as fd:
            fd.write(force_bString(self.eicar))

        try:
            viruses = self.scan_file(tempfilename, 'lint')
        except Exception as e:
            print(e)
            return False

        try:
            os.remove(tempfilename)
        except Exception:
            pass

        try:
            for fname, virus in iter(viruses.items()):
                print("F-Prot AV (file mode): Found virus: %s in %s" % (virus, fname))
                if "EICAR" in virus:
                    return True
                else:
                    print("Couldn't find EICAR in tmp file: %s" % fname)
                    return False
        except Exception as e:
            print(e)
            return False


class CyrenPlugin(AVScannerPlugin):
    """ This plugin passes suspects to a Cyren Antivirus scan daemon (csamd)

Prerequisites: Cyren Antivirus must be installed and running, not necessarily on the same box as fuglu though.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where the ICAP server runs',
            },

            'port': {
                'default': '1344',
                'description': "tcp port or path to unix socket",
            },

            'timeout': {
                'default': '10',
                'description': 'socket timeout',
            },

            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned. ",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },

            'enginename': {
                'default': '',
                'description': 'set custom engine name (defaults to %s)' % self.enginename,
            },
        }
        self.enginename = 'cyren'
        self.logger = self._logger()

    def __str__(self):
        return "Cyren AV"

    def _parse_result(self, result, suspectid):
        dr = {}
        result = force_uString(result.strip())
        self.logger.debug(f'{suspectid} cyren sez {result}')
        #daemon_status, scan_status, obj, message = re.split('\s', result, 3)
        fields = re.split(r'\s', result)
        if len(fields) == 3:
            daemon_status, scan_status, obj = fields
            message = None
        else:
            daemon_status = fields[0]
            scan_status = fields[1]
            #obj = fields[2]
            message = ' '.join(fields[3:])

        if ':' in daemon_status:
            daemon_status = daemon_status.rsplit(':')[-1]

        if daemon_status != 'OK' or scan_status == 'ERROR':
            self.logger.warning(f'{suspectid} scanner errror, got {daemon_status} {scan_status}')
            return None  # or raise exception?
        if scan_status != 'INFECTED':
            self.logger.debug(f'{suspectid} message not infected, got {scan_status}')
            return None

        dr['stream'] = message
        return dr

    def scan_stream(self, content, suspectid='(N/A)'):
        """
        Scans given byte buffer (file content). May raise an exception on errors.
        :param content: file content as string
        :param suspectid: suspect.id of currently processed suspect
        :return: None if no virus is found, else a dict filename -> virusname
        """
        sock = self.__init_socket__()
        remainingbytes = force_bString(content)
        buflen = len(remainingbytes)

        sock.sendall(force_bString('INSTREAM %s\n' % buflen))
        reply = sock.recv(20000)
        if reply != b'OK SEND_DATA\n':
            self.logger.warning(f'{suspectid} Cyren did not respond OK, got {force_uString(reply.strip())}')
            return None

        maxtime = time.time() + self.config.getint(self.section, 'timeout')
        default_chunk_size = min(buflen, 20480)
        iChunk = 0
        while len(remainingbytes) > 0:
            if time.time() > maxtime:
                raise TimeoutError('Timeout sending to AV daemon')
            iChunk = iChunk + 1
            chunklength = min(default_chunk_size, len(remainingbytes))
            chunkdata = remainingbytes[:chunklength]
            remainingbytes = remainingbytes[chunklength:]
            packsize = struct.pack(b'!I', chunklength)
            msg = packsize + chunkdata
            sock.sendall(msg)
        sock.sendall(struct.pack(b'!I', 0))

        resp = sock.recv(20000)
        self._close_socket(sock)
        dr = self._parse_result(resp, suspectid)
        return dr

    def lint_ping(self):
        try:
            sock = self.__init_socket__()
        except Exception as e:
            print("Could not contact csamd: %s" % (str(e)))
            return False
        sock.sendall(force_bString('PING\n'))
        result = sock.recv(20000)
        print("Got Pong: %s" % force_uString(result))
        if result.strip() != b'PONG':
            print("Invalid PONG: %s" % force_uString(result))
        self._close_socket(sock)
        return True

    def lint(self):
        allok = self.check_config() and self.lint_ping() and self.lint_eicar()
        return allok


class HashesFile(FileList):
    def _parse_lines(self, lines):
        hashes = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split(None, 1)
                    hashes[key] = value
                except ValueError as e:
                    self.logger.error(f'invalid line: {line} due to {str(e)}')
        return hashes


class FuzzyHashCheck(AVScannerPlugin):
    """Checks attachments fuzzy hash checksum (e.g. ssdeep) against a database of known malware fuzzy hashes"""
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        
        self.requiredvars = {
            'dbconnectstring': {
                'default': '',
                'description': 'database url, e.g. mysql://root@localhost/ssdeep',
            },
            
            'dbsqlquery': {
                'default': "SELECT ssdeep,filename FROM hashinfo",
                'description': 'database query',
            },
            
            'dbfilepath': {
                'default': '',
                'description': 'database query',
            },
            
            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned.  ",
            },
            
            'threshold': {
                'default': '75',
                'description': 'ssdeep lock threshold',
            },
            
            'minattachmentsize': {
                'default': '5',
                'description': 'minimum attachment size',
            },
            
            'maxattachmentsize': {
                'default': '5000000',
                'description': 'maximum attachment size',
            },
            
            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },
            
            'archivecontentmaxsize': {
                'default': '5000000',
                'description': 'only extract and examine files up to this amount of (uncompressed) bytes',
            },
            
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
            
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
            
            'filenamesrgx': {
                'default': r'\.(exe|scr|com|pif)$',
                'description': 'regex of filenames to be checked',
            },
            
            'virusnametemplate': {
                'default': 'zeroday.FZH/sc${score}',
                'description': 'template of virus name',
            },

            'enginename': {
                'default': '',
                'description': f'set custom engine name (defaults to {self.enginename})',
            },

            'hashalgo': {
                'default': 'ssdeep',
                'description': f'fuzzy hash algorithm to use. available: {", ".join(list(self.check_functions.keys()))}',
            },
        }
        self.logger = self._logger()
        self.hashes_file = None
        self.regex_cache = {}
        self.archive_passwords = {}
        self.enginename = 'fuzzyhash'
    
    def __str__(self):
        return "FuzzyHash"
    
    def examine(self, suspect):
        if not HAVE_SSDEEP:
            return DUNNO
        if self._check_too_big(suspect):
            return DUNNO
        
        content = suspect.get_source()
        self.archive_passwords[suspect.id] = suspect.get_tag('archive_password', [])
        try:
            viruses = self.scan_stream(content, suspect.id)
            actioncode, message = self._virusreport(suspect, viruses)
            del self.archive_passwords[suspect.id]
            return actioncode, message
        except Exception as e:
            self.logger.warning(f'{suspect.id} Error encountered while checking fuzzyhash: {e.__class__.__name__}: {str(e)}')
        
        del self.archive_passwords[suspect.id]
        return self._problemcode()
    
    def lint(self):
        if not HAVE_SSDEEP:
            print('ERROR: ssdeep library missing')
            return False
        ok = self.check_config()
        if ok:
            hashalgo = self.config.get(self.section, 'hashalgo')
            if hashalgo not in self.check_functions:
                print(f'ERROR: unsupported hashalgo {hashalgo}')
                ok = False
            
            dbfile = self.config.get(self.section, 'dbfilepath')
            dbconnection = self.config.get(self.section, 'dbconnectstring')
            sqlquery = self.config.get(self.section, 'dbsqlquery')
            if dbfile:
                if not os.path.exists(dbfile):
                    print(f'ERROR: db file {dbfile} not found')
                    ok = False
            elif dbconnection:
                if not sqlquery:
                    print(f'ERROR: db connection given, but not sql query')
                    ok = False
                else:
                    try:
                        session = get_session(dbconnection)
                        session.execute(text('SELECT 1'))
                    except Exception as e:
                        print(f'ERROR: failed to connect to database due to {e.__class__.__name__}: {str(e)}')
                        ok = False
            else:
                print(f'ERROR: neither dbfile nor sql connection specified - cannot load signatures')
                ok = False
        return ok
    
    def scan_stream(self, content, suspectid='(n/a)', attachmentmanager=None):
        dr = dict()
        
        if attachmentmanager:
            # if sent in, use attachment manager since it has all information and files already
            # extracted and buffered
            attmanager = attachmentmanager
        else:
            # otherwise create the manager from the message
            try:
                msg = email.message_from_string(content, _class=PatchedMessage)
            except TypeError:
                msg = email.message_from_bytes(content, _class=PatchedMessage)
            attmanager = Mailattachment_mgr(msg, suspectid)
        
        for att in attmanager.get_objectlist():
            att_name = att.filename
            if not att.is_archive:  # no mime-type or filename regex matched the current attachment
                self.logger.debug(f'{suspectid} {att_name} skipping: not an archive')
                continue
            
            payload = att.buffer
            att_len = len(payload)
            
            self.logger.debug(f'{suspectid} check {att_name} with length={att_len}')
            if att_len < self.config.getint(self.section, 'minattachmentsize'):
                continue
            if att_len > self.config.getint(self.section, 'maxattachmentsize'):
                continue
            
            archive_passwords = self.archive_passwords.get(suspectid, [])
            if archive_passwords:
                att.archive_passwords = archive_passwords
            if att.filename_generated:
                # if filename was auto-generated, set to None to be consistent with old implementation
                att_name = None
            
            try:
                self.logger.debug(f'{suspectid} handle_archive')
                filename, score = self.handle_archive(att, suspectid)
                if filename is not None:
                    att_ascii_name = att.get_mangled_filename(keepending=True)
                    ext_ascii_name = att.mangle_filename(filename, keepending=True)
                    key = f'{att_ascii_name if att_name is not None else att_name}->{ext_ascii_name}'
                    template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
                    value = template.safe_substitute({'score': score, 'att_ascii_name': att_ascii_name, 'ext_ascii_name': ext_ascii_name})
                    dr[key] = value
                    return dr
            
            except Exception as e:
                message = str(e)
                if 'password' in message:
                    pass  # hide error message due to encrypted archive
                elif 'compression type' in message:
                    pass  # hide error message due to unsupported pkzip type 9 (deflate64) etc
                elif 'Bad magic number' in message:
                    pass  # hide errors from invalid zip files
                elif 'BadRarFile' in message:
                    pass  # hide errors from invalid rar files
                else:
                    # self.logger.error("could not handle attachment: ")
                    raise
        return None
    
    def _get_hashes_sql(self):
        session = get_session(self.config.get(self.section, 'dbconnectstring'))
        sqlquery = self.config.get(self.section, 'dbsqlquery')
        res = session.execute(text(sqlquery))
        known_hashes = {}
        for row in res:
            known_hashes[row[0]] = row[1]
        return known_hashes
    
    def _get_hashes_file(self, dbfile):
        hashes = {}
        if self.hashes_file is None:
            self.hashes_file = HashesFile(dbfile)
        if self.hashes_file is not None:
            hashes = self.hashes_file.get_list()
        return hashes
    
    def _get_hashes(self):
        hashes = {}
        if self.config.get(self.section, 'dbconnectstring'):
            hashes.update(self._get_hashes_sql())
        dbfile = self.config.get(self.section, 'dbfilepath')
        if dbfile and os.path.exists(dbfile):
            hashes.update(self._get_hashes_file(dbfile))
        return hashes
    
    def _compare_ssdeep(self, suspectid, known_hashes, fuzzyhash):
        found_score = 0
        found_filename = None
        if HAVE_SSDEEP:
            for knownhash, filename in iter(known_hashes.items()):
                try:
                    score = ssdeep.compare(knownhash, fuzzyhash)
                    
                    if score >= self.config.getint(self.section, 'threshold') and score > found_score:
                        found_score = score
                        found_filename = filename
                except ssdeep.InternalError as e:
                    self.logger.error(f'{suspectid} failed to compare ssdeep hashes. knownhash={knownhash} fuzzyhash={fuzzyhash} error={str(e)}')
        else:
            self.logger.error(f'{suspectid} failed to compare ssdeep hashes - ssdeep not installed')
        return found_filename, found_score
    
    check_functions = {
        'ssdeep': _compare_ssdeep,
    }
    
    def handle_archive(self, att, suspectid='(n/a)'):
        """Return the known filename with the hightest hitrate (above the configured threshold or None if no file reaches configured threshold"""
        
        att_name = att.filename
        att_ascii_name = att.get_mangled_filename(keepending=True)
        found_filename = None
        found_score = 0
        
        hashalgo = self.config.get(self.section, 'hashalgo')
        cmpfunc = self.check_functions[hashalgo]
        
        archivecontentmaxsize = self.config.getint(self.section, 'archivecontentmaxsize')
        regexstring = self.config.get(self.section, 'filenamesrgx')
        if regexstring in self.regex_cache:
            rgx = self.regex_cache[regexstring]
        else:
            rgx = re.compile(regexstring)
            self.regex_cache[regexstring] = rgx
        known_hashes = self._get_hashes()
        
        if att.archive_handle is None:
            self.logger.info(f'{suspectid} {att_name} invalid archive?')
        
        namelist = att.fileslist_archive
        
        for name in namelist:
            if not rgx.search(name):
                self.logger.debug(f'{suspectid} name: {name} not matching pattern: {rgx.pattern}')
                continue
            
            noextractinfo = NoExtractInfo()
            extracted_object = att.get_archive_obj(name, archivecontentmaxsize, noextractinfo=noextractinfo)
            if not extracted_object:
                for item in noextractinfo.get_filtered():
                    try:
                        filename, message = item
                        self.logger.info(f'{suspectid} file {name} in archive {att_ascii_name} failed to extract due to {message}')
                    except Exception as e:
                        self.logger.info(f'{suspectid} file {name} in archive {att_ascii_name} failed to extract due to {e.__class__.__name__}: {str(e)}')
                continue
            
            fuzzyhash = extracted_object.get_checksum(hashalgo)
            ext_ascii_name = extracted_object.get_mangled_filename(keepending=True)
            self.logger.debug(f'{suspectid} sshash={fuzzyhash} filename={ext_ascii_name}')
            found_filename, found_score = cmpfunc(self, suspectid, known_hashes, fuzzyhash)
        
        return found_filename, found_score



if __name__ == '__main__':
    if 'drweb' in sys.argv:
        drweb_main()
