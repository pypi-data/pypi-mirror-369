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
from fuglu.shared import AVScannerPlugin, string_to_actioncode, DUNNO, actioncode_to_string, FileList
from fuglu.stringencode import force_bString, force_uString
from fuglu.protocolbase import set_keepalive_linux
import socket
import os
import struct
import threading
import errno
import subprocess # nosemgrep CWE-78
import time
import math

threadLocal = threading.local()
# it's probably a good idea to re-establish the connection occasionally
MAX_SCANS_PER_SOCKET = 5000


class ClamavTimeout(Exception):
    pass


class ClamavPlugin(AVScannerPlugin):

    """This plugin passes suspects to a clam daemon. 

Actions: This plugin will delete infected messages. If clamd is not reachable or times out, messages can be DEFERRED.

Prerequisites: You must have clamd installed (for performance reasons I recommend it to be on the same box, but this is not absoluely necessary)

Notes for developers:


Tags:

 * sets ``virus['ClamAV']`` (boolean)
 * sets ``ClamavPlugin.virus`` (list of strings) - virus names found in message
"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where clamd runs',
            },

            'port': {
                'default': '3310',
                'description': "tcp port number or path to clamd.sock for unix domain sockets\nexample /var/lib/clamav/clamd.sock or on ubuntu: /var/run/clamav/clamd.ctl ",
            },

            'timeout': {
                'default': '30',
                'description': 'socket timeout',
            },

            'pipelining': {
                'default': 'False',
                'description': "*EXPERIMENTAL*: Perform multiple scans over the same connection. May improve performance on busy systems.",
            },

            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned.  \nshould match the 'StreamMaxLength' config option in clamd.conf ",
            },
            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },

            'virusaction_unofficial': {
                'default': '',
                'description': "action if infection is detected by UNOFFICIAL (3rd party) signature (DUNNO, REJECT, DELETE). if left empty use standard virusaction",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },

            'clamscanfallback': {
                'default': 'False',
                'description': "*EXPERIMENTAL*: fallback to clamscan if clamd is unavailable. YMMV, each scan can take 5-20 seconds and massively increase load on a busy system.",
            },

            'clamscan': {
                'default': '/usr/bin/clamscan',
                'description': "the path to clamscan executable",
            },

            'clamscantimeout': {
                'default': '30',
                'description': "process timeout",
            },

            'skip_on_previous_virus': {
                'default': 'none',
                'description': 'define AVScanner engine names causing current plugin to skip if they found already a virus',
            },

            'skiplist_file': {
                'default': '',
                'description': 'path to file with signature names that can be skipped if message is welcomelisted. list one signature per line, signature is case sensitive',
            },

            'enginename': {
                'default': '',
                'description': f'set custom engine name (defaults to {self.enginename})',
            },
        }
        self.enginename = 'ClamAV'
        # logger after engine so we can use the enginename in the logger...
        self.logger = self._logger()
        self.skiplist = None

    def _init_skiplist(self):
        if self.skiplist is None:
            skiplist_file = self.config.get(self.section, 'skiplist_file')
            if skiplist_file:
                self.skiplist = FileList(skiplist_file)

    def _check_skiplist(self, suspect, viruses):
        """
        if message is welcomelisted, skip defined signature hits
        :param suspect: the suspect object
        :param viruses: dict of virus scan results
        :return: (bool) True if hit should not be counted
        """
        self._init_skiplist()
        if viruses and self.skiplist and suspect.is_welcomelisted():
            skiplist = self.skiplist.get_list()
            virusnames = list(viruses.values())
            if len(virusnames) == 1 and virusnames[0] in skiplist:
                self.logger.info(f"{suspect.id} got hit on {','.join(virusnames)} but is skiplisted")
                return True
        return False

    def __str__(self):
        classname = self.__class__.__name__
        if self.section == classname:
            return "Clam AV"
        else:
            return f'Clam AV - {self.section}'

    def examine(self, suspect):
        if self._check_too_big(suspect):
            return DUNNO

        skip = self._skip_on_previous_virus(suspect)
        if skip:
            self.logger.info(f"{suspect.id} {skip}")
            return DUNNO

        viruses = {}
        success = False
        content = suspect.get_source()
        # prefix source with a well-known mail header so clamav really recognises data as type mime
        content = suspect.prepend_header_to_source('Return-Path', f'<{suspect.from_address or ""}>', content)

        attempts = max_attempts = max(self.config.getint(self.section, 'retries'), 1)
        # for i in range(0, self.config.getint(self.section, 'retries')):
        while attempts:
            attempts -= 1
            try:
                viruses = self.scan_stream(content, suspect.id)
                success = True
                break
            except (socket.error, socket.timeout, ConnectionRefusedError) as e:
                self.__invalidate_socket()

                # don't warn the first times if it's just a broken pipe which
                # can happen with the new pipelining protocol
                msg = f"{suspect.id} Problem encountered while contacting clamd " \
                      f"(try {max_attempts - attempts}/{max_attempts}): {e.__class__.__name__} {str(e)}"
                if attempts:
                    if not e.errno == errno.EPIPE:
                        self.logger.warning(msg)
                else:
                    self.logger.error(msg)
            except ClamavTimeout as e:
                msg = f"Clamav timeout raised (try {max_attempts - attempts}/{max_attempts}): {str(e)}"
                self.logger.warning(msg) if attempts else self.logger.error(msg)
                suspect.tags[f'{self.enginename}.timeout'] = max_attempts - attempts
                self.__invalidate_socket()
            except Exception as e:
                self.logger.exception(e)
                self.__invalidate_socket()

        if not success:
            self.logger.error(f"{suspect.id} Clamdscan failed after {max_attempts} retries")

        if not success and self.config.getboolean(self.section, 'clamscanfallback'):
            try:
                viruses = self.scan_shell(content)
                success = True
            except Exception:
                self.logger.error(f'{suspect.id} failed to scan using fallback clamscan')

        if not success:
            return self._problemcode()
        elif self._check_skiplist(suspect, viruses):
            return DUNNO
        else:
            actioncode, message = self._virusreport(suspect, viruses)
            if viruses and self.config.get(self.section, 'virusaction_unofficial'):
                actioncode = self._virusaction_unofficial(viruses, actioncode)
            return actioncode, message

    def _virusaction_unofficial(self, viruses, actioncode):
        # override virusaction if one of the virus hits is caused by "UNOFFICIAL" signature
        for filename in viruses:
            signame = viruses[filename]
            if signame.endswith('.UNOFFICIAL'):
                virusaction = self.config.get(self.section, 'virusaction_unofficial')
                actioncode = string_to_actioncode(virusaction, self.config)
                break
        return actioncode

    def scan_shell(self, content):
        clamscan = self.config.get(self.section, 'clamscan')
        timeout = self.config.getint(self.section, 'clamscantimeout')

        if not os.path.exists(clamscan):
            raise Exception(f'could not find clamscan executable in {clamscan}')

        try:
            process = subprocess.Popen([clamscan, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)  # file data by pipe
            def kill_proc(p): return p.kill()
            timer = threading.Timer(timeout, kill_proc, [process])
            timer.start()
            stdout = process.communicate(force_bString(content))[0]
            process.stdin.close()
            exitcode = process.wait()
            timer.cancel()
        except Exception:
            exitcode = -1
            stdout = b''

        if exitcode > 1:  # 0: no virus, 1: virus, >1: error, -1 subprocess error
            raise Exception('clamscan error')
        elif exitcode < 0:
            raise Exception(f'clamscan timeout after {timeout}s')

        dr = {}

        for line in stdout.splitlines():
            line = line.strip()
            if line.endswith(b'FOUND'):
                filename, virusname, found = line.rsplit(None, 2)
                filename = force_uString(filename.rstrip(b':'))
                dr[filename] = force_uString(virusname)

        if dr == {}:
            return None
        else:
            return dr

    def scan_stream(self, content, suspectid="(NA)"):
        """
        Scan byte buffer

        return either :
          - (dict) : {filename1: "virusname"}
          - None if no virus found
          - raises Exception if something went wrong
        """
        pipelining = self.config.getboolean(self.section, 'pipelining')
        s = self.__init_socket__(oneshot=not pipelining)
        s.sendall(b'zINSTREAM\0')
        remainingbytes = force_bString(content)
        default_chunk_size = min(len(remainingbytes), 20480)
        maxtime = time.time() + self.config.getint(self.section, 'timeout')

        numChunksToSend = math.ceil(len(remainingbytes)/default_chunk_size)
        iChunk = 0
        chunklength = 0
        self.logger.debug(f'{suspectid} sending message in {numChunksToSend} chunks of size {default_chunk_size} bytes')

        while len(remainingbytes) > 0:
            if time.time() > maxtime:
                raise TimeoutError(f'{suspectid} Timeout sending to AV daemon')
            iChunk = iChunk + 1
            chunklength = min(default_chunk_size, len(remainingbytes))
            #self.logger.debug('sending chunk %u/%u' % (iChunk,numChunksToSend))
            #self.logger.debug('sending %s byte chunk' % chunklength)
            chunkdata = remainingbytes[:chunklength]
            remainingbytes = remainingbytes[chunklength:]
            s.sendall(struct.pack(b'!L', chunklength))
            s.sendall(chunkdata)
        self.logger.debug(f'{suspectid} sent chunk {iChunk}/{numChunksToSend}, last number of bytes sent was {chunklength}')
        self.logger.debug(f'{suspectid} All chunks sent, sending 0 - size to tell ClamAV the whole message has been sent')
        s.sendall(struct.pack(b'!L', 0))
        self.logger.debug(f'{suspectid} 0 has been sent, now wait for answer')
        dr = {}

        result = force_uString(self._read_until_delimiter(s, suspectid)).strip()
        self.logger.debug(f'{suspectid} got result {result}')

        if result.startswith('INSTREAM size limit exceeded'):
            raise Exception(f"{suspectid} Clamd size limit exeeded. Make sure fuglu's clamd maxsize config is not larger than clamd's StreamMaxLength")
        if result.startswith('UNKNOWN'):
            raise Exception(f"{suspectid} Clamd doesn't understand INSTREAM command. very old version?")

        if pipelining:
            try:
                ans_id, filename, virusinfo = result.split(':', 2)
                filename = force_uString(filename.strip())  # use unicode for filename
                virusinfo = force_uString(virusinfo.strip())  # use unicode for virusinfo
            except Exception:
                raise Exception(f"{suspectid} Protocol error, could not parse result: {result}")

            threadLocal.expectedID += 1
            if threadLocal.expectedID != int(ans_id):
                raise Exception(f"{suspectid} Commands out of sync - expected ID {threadLocal.expectedID} - got {ans_id}")

            if virusinfo[-5:] == 'ERROR':
                raise Exception(virusinfo)
            elif virusinfo != 'OK':
                dr[filename] = virusinfo.replace(" FOUND", '')

            if threadLocal.expectedID >= MAX_SCANS_PER_SOCKET:
                try:
                    s.sendall(b'zEND\0')
                    s.close()
                finally:
                    self.__invalidate_socket()
        else:
            filename, virusinfo = result.split(':', 1)
            filename = force_uString(filename.strip())  # use unicode for filename
            virusinfo = force_uString(virusinfo.strip())  # use unicode for virus info
            if virusinfo[-5:] == 'ERROR':
                raise Exception(virusinfo)
            elif virusinfo != 'OK':
                dr[filename] = virusinfo.replace(" FOUND", '')
            s.close()

        if dr == {}:
            return None
        else:
            return dr

    def _read_until_delimiter(self, sock, suspectID="(NA)"):
        data = b''
        maxFailedAttempts = 40
        failedAttempt = 0
        timeout = self.config.getint(self.section, 'timeout')
        readtimeout = min(timeout*3, timeout+30)  # extra timeout condition
        starttime = time.time()

        while True:
            try:
                #self.logger.debug(f"{suspectID}: try to receive chunk")
                chunk = sock.recv(4096)
                #self.logger.debug(f"{suspectID}: Got chunk of length {len(chunk)}")
                if len(chunk) == 0:
                    # Extra timeout condition here because we don't reach the else
                    # statement and won't do this extra check. This happened in a docker
                    # swarm setup with multiple clam services during an update
                    runtime = time.time() - starttime
                    if runtime > readtimeout:
                        raise ClamavTimeout(f"{suspectID} 0-chunk-length read timeout after {runtime:.2f}s")
                    time.sleep(0.01) # no need to hammer
                    continue
                data += chunk
                if chunk.endswith(b'\0'):
                    self.logger.debug(f"{suspectID} Got all chunks... data length {len(data)}")
                    break
                if b'\0' in chunk:
                    raise Exception(f"{suspectID} Protocol error: got unexpected additional data after delimiter")
            except socket.error as e:
                # looks like there can be a socket error when we try to connect too quickly after sending, so
                # better retry several times
                # Got this idea from pyclamd, see:
                # https://bitbucket.org/xael/pyclamd/src/2089daa540e1343cf414c4728f1322c96a615898/pyclamd/pyclamd.py?at=default&fileviewer=file-view-default#pyclamd.py-614
                # There the sleep for 0.01 [s] for 5 tries, so 0.05 [s] in total to wait. But I'm happy to set a
                # maximum of 1 second by 40*0.025 [s] if this helps to avoid a complete rescan of the message
                time.sleep(0.025)
                failedAttempt += 1
                self.logger.warning(f"{suspectID} Failed receive attempt {failedAttempt}/{maxFailedAttempts}: {str(e)}")
                if failedAttempt == maxFailedAttempts:
                    raise ClamavTimeout(f"{suspectID} Max failed received attempts ({maxFailedAttempts}): {str(e)}")

            # Sometimes we get one socket error and after that we never get a proper answer to satisfy
            # break or exception condition in try block, neither are there subsequent socket errors.
            # This can lead to an endless loop where a worker remains forever in this while loop,
            # rendering the worker useless and causing high cpu load. We thus add this additional
            # loop termination condition.
            runtime = time.time() - starttime
            if runtime > readtimeout:
                raise ClamavTimeout(f"{suspectID}: Read timeout after {runtime:.2f}s > {readtimeout:.2f}s")

        return data[:-1]  # remove \0 at the end

    def __invalidate_socket(self):
        threadLocal.clamdsocket = None
        threadLocal.expectedID = 0

    def __init_socket__(self, oneshot=False):
        """initialize a socket connection to clamd using host/port/file defined in the configuration
        this connection is initialized with clamd's "IDSESSION" and cached per thread

         set oneshot=True to get a socket without caching it and without initializing it with an IDSESSION
         """

        existing_socket = getattr(threadLocal, 'clamdsocket', None)

        socktimeout = self.config.getint(self.section, 'timeout')

        if existing_socket is not None and not oneshot:
            existing_socket.settimeout(socktimeout)
            return existing_socket

        clamd_HOST = self.config.get(self.section, 'host', resolve_env=True)
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
            s.settimeout(socktimeout)
            try:
                s.connect(sock)
            except socket.error:
                raise socket.error(f'Could not reach clamd using unix socket {sock}')
        else:
            clamd_PORT = self.config.getint(self.section, 'port')
            proto = socket.AF_INET
            if ':' in clamd_HOST:
                proto = socket.AF_INET6
            s = socket.socket(proto, socket.SOCK_STREAM)
            s.settimeout(socktimeout)
            try:
                s.connect((clamd_HOST, clamd_PORT))
            except socket.error:
                raise socket.error(f'Could not reach clamd using network ({clamd_HOST}:{clamd_PORT})')
            # set keepalive options
            set_keepalive_linux(s)

        # initialize an IDSESSION
        if not oneshot:
            s.sendall(b'zIDSESSION\0')
            threadLocal.clamdsocket = s
            threadLocal.expectedID = 0
        return s

    def lint(self):
        viract = self.config.get(self.section, 'virusaction')
        print("Virusaction: %s" % actioncode_to_string(
            string_to_actioncode(viract, self.config)))
        allok = self.check_config() and self.lint_ping() and self.lint_version() and self.lint_eicar()

        if self.config.getboolean(self.section, 'clamscanfallback'):
            print('WARNING: Fallback to clamscan enabled')
            starttime = time.time()
            allok = self.lint_eicar('scan_shell')
            if allok:
                runtime = time.time()-starttime
                print('clamscan scan time: %.2fs' % runtime)

        # print lint info for skip
        self.lintinfo_skip()
        return allok

    def lint_ping(self):
        try:
            s = self.__init_socket__(oneshot=True)
        except Exception as e:
            print("Could not contact clamd: %s" % (str(e)))
            return False
        s.sendall(force_bString('PING'))
        result = s.recv(20000)
        result = force_uString(result.strip())
        print(f"Got Pong: {result}")
        if result != 'PONG':
            print(f"Invalid PONG: {result}")
        return True

    def lint_version(self):
        try:
            s = self.__init_socket__(oneshot=True)
        except Exception:
            return False
        s.sendall(b'VERSION')
        result = s.recv(20000)
        print("Got Version: %s" % force_uString(result.strip()))
        return True
