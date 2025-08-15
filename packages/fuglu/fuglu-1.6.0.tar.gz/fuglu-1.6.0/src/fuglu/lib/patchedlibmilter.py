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
#
import libmilter as lm
import socket
import asyncio
import struct


class ASYNCMilterProtocol(lm.MilterProtocol):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, opts=0, protos=0):
        super().__init__(opts=opts, protos=protos)
        self.reader = reader
        self.writer = writer

        if self._sockLock:
            del self._sockLock
            self._sockLock = None

    async def send(self, msg):
        """
        A simple wrapper for self.transport.sendall
        """
        # self._sockLock.acquire()
        try:
            self.writer.write(msg)
            await self.writer.drain()
        except AttributeError as e:
            emsg = f'AttributeError sending {msg}: {e}'
            self.log(emsg)
        except socket.error as e:
            emsg = f'Socket Error sending {msg}: {e}'
            self.log(emsg)
        except Exception as e:
            emsg = f'Socket Error sending {msg}: {e}'
            self.log(emsg)

        # self._sockLock.release()

    async def _procCmdAndData(self, cmds):
        skipNum = 0
        toSend = ''
        for i, cmd in enumerate(cmds):
            toSend = ''
            mtype = ''
            firstLet = cmd[:1]
            if skipNum:
                skipNum -= 1
                continue
            elif firstLet == lm.SMFIC_OPTNEG:
                lm.debug('MTA OPTS: %r' % cmd, 4, self.id)
                toSend = await self._negotiate(cmd)
                lm.debug(f'toSend: {toSend}')
            elif firstLet == lm.SMFIC_ABORT:
                await self._abort()
                continue
            elif firstLet == lm.SMFIC_QUIT or \
                    firstLet == lm.SMFIC_QUIT_NC:
                await self._close()
                continue
            elif firstLet == lm.SMFIC_MACRO:
                # We have a command macro.  We just store for when the
                # command comes back up
                self._lastMacro = cmd
                continue
            elif firstLet in self._MACMAP:
                mtype = cmd[:1]
            if toSend and not mtype:
                # Basically, we just want to send something back
                lm.debug('toSend is defined -> pass')
                pass
            elif mtype not in self._MACMAP:
                raise lm.UnsupportedError('Unsupported MACRO in '
                                          '%d: %s (%s)' % (self.id, mtype, cmd))
            else:
                lmtype = None
                if self._lastMacro is not None and len(self._lastMacro) > 1:
                    lmtype = self._lastMacro[1:2]
                d = [cmd]
                macro = None
                if lmtype == mtype:
                    macro = self._lastMacro
                if mtype in lm.protoMap:
                    nc = lm.optCBs[lm.protoMap[mtype]][0]
                    nr = lm.optCBs[lm.protoMap[mtype]][1]
                    if self.protos & nc:
                        lm.debug('No callback set for %r' % self._MACMAP[mtype],
                                 4, self.id)
                        # There is a nocallback set for this, just continue
                        continue
                    elif self.protos & nr:
                        # No reply for this, just run it and discard
                        # the response
                        lm.debug('No response set for %r' % self._MACMAP[mtype],
                                 4, self.id)
                        await self._MACMAP[mtype](macro, d)
                        continue
                # Run it and send back to the MTA
                lm.debug('Calling %r for qid: %s' % (self._MACMAP[mtype],
                                                     self._qid), 4, self.id)
                toSend = await self._MACMAP[mtype](macro, d)
                if not toSend:
                    # If there was not a return value and we get here, toSend
                    # should be set to CONTINUE
                    toSend = lm.CONTINUE
            if toSend and not isinstance(toSend, lm.Deferred):
                lm.debug(f'Want to send buffer {toSend}, make async call to send...')
                await self.send(toSend)
                lm.debug(f'after waiting...')

    async def addRcpt(self, rcpt, esmtpAdd=b''):
        """
        This will tell the MTA to add a recipient to the email

        NOTE: This can ONLY be called in eob()
        """
        if esmtpAdd:
            if not lm.SMFIF_ADDRCPT_PAR & self._opts & self._mtaOpts:
                print('Add recipient par called without the proper opts set')
                return
            req = lm.SMFIR_ADDRCPT_PAR + rcpt + b'\0' + esmtpAdd + b'\0'
            req = lm.pack_uint32(len(req)) + req
        else:
            if not lm.SMFIF_ADDRCPT & self._opts & self._mtaOpts:
                print('Add recipient called without the proper opts set')
                return
            req = lm.SMFIR_ADDRCPT + rcpt + b'\0'
            req = lm.pack_uint32(len(req)) + req
        self.writer.write(req)
        await self.writer.drain()

    async def delRcpt(self, rcpt):
        """
        This will tell the MTA to delete a recipient from the email

        NOTE: This can ONLY be called in eob()
        NOTE: The recipient address must be EXACTLY the same as one
        of the addresses received in the rcpt() callback'
        """
        if not lm.SMFIF_DELRCPT & self._opts & self._mtaOpts:
            print('Delete recipient called without the proper opts set')
            return
        req = lm.SMFIR_DELRCPT + rcpt + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def replBody(self, body):
        """
        This will replace the body of the email with a new body

        NOTE: This can ONLY be called in eob()
        """
        if not lm.SMFIF_CHGBODY & self._opts & self._mtaOpts:
            print('Tried to change the body without setting the proper option')
            return
        req = lm.SMFIR_REPLBODY + body
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def addHeader(self, key, val):
        """
        This will add a header to the email in the form:
            key: val

        NOTE: This can ONLY be called in eob()
        """
        if not lm.SMFIF_ADDHDRS & self._opts & self._mtaOpts:
            print('Add header called without the proper opts set')
            return
        req = lm.SMFIR_ADDHEADER + key.rstrip(b':') + b'\0' + val + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def chgHeader(self, key, val=b'', index=1):
        """
        This will change a header in the email.  The "key" should be
        exactly what was received in header().  If "val" is empty (''),
        the header will be removed.  "index" refers to which header to
        remove in the case that there are multiple headers with the
        same "key" (Received: is one example)

        NOTE: This can ONLY be called in eob()
        """
        if not lm.SMFIF_CHGHDRS & self._opts & self._mtaOpts:
            print('Change headers called without the proper opts set')
            return
        req = lm.SMFIR_CHGHEADER + lm.pack_uint32(index) + \
            key.rstrip(b':') + b'\0' + val + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def quarantine(self, msg=b''):
        """
        This tells the MTA to quarantine the message (put it in the HOLD
        queue in Postfix).

        NOTE: This can ONLY be called in eob()
        """
        if not lm.SMFIF_QUARANTINE & self._opts & self._mtaOpts:
            print('Quarantine called without the proper opts set')
            return
        req = lm.SMFIR_QUARANTINE + msg + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    def setReply(self, rcode, xcode, msg):
        raise DeprecationWarning("Don't use this, use sendReply instead")

    async def sendReply(self, rcode, xcode, msg):
        """
        Sets the reply that the MTA will use for this message.
        The "rcode" is the 3 digit code to use (ex. 554 or 250).
        The "xcode" is the xcode part of the reply (ex. 5.7.1 or 2.1.0).
        The "msg" is the text response.
        """
        req = lm.SMFIR_REPLYCODE + rcode + b' ' + xcode + b' ' + msg + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def chgFrom(self, frAddr, esmtpAdd=b''):
        """
        This tells the MTA to change the from address, with optional
        ESMTP extensions

        NOTE: This can ONLY be called in eob()
        """
        if not lm.SMFIF_CHGFROM & self._opts & self._mtaOpts:
            print('Change from called without the proper opts set')
            return
        req = lm.SMFIR_CHGFROM + frAddr + b'\0' + esmtpAdd + b'\0'
        req = lm.pack_uint32(len(req)) + req

        self.writer.write(req)
        await self.writer.drain()

    async def skip(self):
        """
        This tells the MTA that we don't want any more of this type of
        callback.

        This option must be set as well

        THIS CAN ONLY BE CALLED FROM THE body() callback!!
        """
        if not lm.SMFIP_SKIP & self.protos & self._mtaProtos:
            print('Skip called without the proper opts set')
            return
        req = lm.pack_uint32(1) + lm.SMFIR_SKIP

        self.writer.write(req)
        await self.writer.drain()

    #
    # Raw data callbacks {{{
    # DO NOT OVERRIDE THESE UNLESS YOU KNOW WHAT YOU ARE DOING!!
    #
    async def _negotiate(self, cmd):
        """
        Handles the opening optneg packet from the MTA
        """
        cmd = cmd[1:]
        v, mtaOpts, mtaProtos = struct.unpack('!III', cmd)
        self._mtaVersion = v
        self._mtaOpts = mtaOpts
        self._mtaProtos = mtaProtos
        return self._getOptnegPkt()

    async def _connect(self, cmd, data):
        """
        Parses the connect info from the MTA, calling the connect()
        method with (<reverse hostname> , <ip family> , <ip addr> ,
            <port> , <cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        data = data[0]
        hostname = ''
        family = ''
        port = -1
        ip = ''
        if data:
            lm.checkData(data, lm.SMFIC_CONNECT)
            hostname, rem = lm.readUntilNull(data[1:])
            # rem[0] stores the ascii code of the family character as an integer
            # for example, ascii character '4' has integer value 52.
            family = rem[0:1]
            if family != lm.SMFIA_UNKNOWN:
                port = lm.unpack_uint16(rem[1:3])
                ip = rem[3:-1]
        return await self.connect(hostname, family, ip, port, md)

    async def _helo(self, cmd, data):
        """
        Parses the helo info from the MTA and calls helo() with
        (<helo name>)
        """
        self.log(f"in _helo: cmd: {cmd}, data: {data}")
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        data = data[0]
        heloname = ''
        if data:
            lm.checkData(data, lm.SMFIC_HELO)
            heloname = data[1:-1]
        return await self.helo(heloname, md)

    async def _mailFrom(self, cmd, data):
        """
        Parses the MAIL FROM info from the MTA and calls mailFrom()
        with (<from addr> , <cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        data = data[0]
        mfrom = ''
        if data:
            mfrom = data[1:-1]
        # Return the mail from address parsed by the MTA, if possible
        if 'mail_addr' in md:
            mfrom = md['mail_addr']
        if 'i' in md:
            self._qid = md['i']
        return await self.mailFrom(mfrom, md)

    async def _rcpt(self, cmd, data):
        """
        Parses the RCPT TO info from the MTA and calls rcpt()
        with (<rcpt addr> , <cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        data = data[0]
        rcpt = ''
        if data:
            rcpt = data[1:-1]
        elif 'rcpt_addr' in md:
            rcpt = md['rcpt_addr']
        if 'i' in md:
            self._qid = md['i']
        return await self.rcpt(rcpt, md)

    async def _header(self, cmd, data):
        """
        Parses the header from the MTA and calls header() with
        (<header name> , <header value> , <cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        data = data[0]
        key = ''
        val = ''
        if 'i' in md:
            self._qid = md['i']
        if data:
            key, rem = lm.readUntilNull(data[1:])
            val, rem = lm.readUntilNull(rem)
            if rem:
                raise lm.UnknownError('Extra data for header: %s=%s (%s)' % (key, val, data))
        return await self.header(key, val, md)

    async def _eoh(self, cmd, data):
        """
        Parses the End Of Header from the MTA and calls eoh() with
        (<cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        if 'i' in md:
            self._qid = md['i']
        return await self.eoh(md)

    async def _data(self, cmd, data):
        """
        Parses the DATA call from the MTA and calls data() with (<cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        if 'i' in md:
            self._qid = md['i']
        return await self.data(md)

    async def _body(self, cmd, data):
        """
        Parses the body chunk from the MTA and calls body() with
        (<body chunk> , <cmdDict>)
        """
        data = data[0]
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        chunk = ''
        if 'i' in md:
            self._qid = md['i']
        if data:
            chunk = data[1:]
        return await self.body(chunk, md)

    async def _eob(self, cmd, data):
        """
        Parses the End Of Body from the MTA and calls eob() with
        (<cmdDict>)
        """
        md = {}
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        if 'i' in md:
            self._qid = md['i']
        ret = await self.eob(md)
        return ret

    async def _close(self, cmd=None, data=None):
        """
        This is a wrapper for close() that checks to see if close()
        has already been called and calls it if it has not.  This
        will also close the transport's connection.
        """
        if not self.closed:
            self.closed = True
            await self.close()

    async def _abort(self):
        """
        This is called when an ABORT is received from the MTA.  It
        calls abort() and then _close()
        """
        self._qid = None
        await self.abort()

    async def _unknown(self, cmd, data):
        """
        Unknown command sent.  Call unknown() with (<cmdDict> , <data>)
        """
        if cmd is not None:
            md = lm.dictFromCmd(cmd[2:])
        md = lm.dictFromCmd(cmd[2:])
        return await self.unknown(md, data)
    # }}}

    ###################
    # Info callbacks  {{{
    # Override these in a subclass
    ###################
    @lm.noCallback
    async def connect(self, hostname, family, ip, port, cmdDict):
        """
        This gets the connection info:

        str:hostname    The reverse hostname of the connecting ip
        str:family      The IP family (L=unix , 4=ipv4 , 6=ipv6 , U=unknown)
        str:ip          The IP of the connecting client
        int:port        The port number of the connecting client
        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('Connect from %s:%d (%s) with family: %s' % (ip, port,
                                                              hostname, family))
        return lm.CONTINUE

    @lm.noCallback
    async def helo(self, heloname, command_dict):
        """
        This gets the HELO string sent by the client

        str:heloname    What the client HELOed as

        Override this in a subclass.
        """
        self.log('HELO: %s' % heloname)
        return lm.CONTINUE

    @lm.noCallback
    async def mailFrom(self, frAddr, cmdDict):
        """
        This gets the MAIL FROM envelope address

        str:frAddr      The envelope from address
        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('MAIL: %s' % frAddr)
        return lm.CONTINUE

    @lm.noCallback
    async def rcpt(self, recip, cmdDict):
        """
        This gets the RCPT TO envelope address

        str:recip       The envelope recipient address
        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('RCPT: %s' % recip)
        return lm.CONTINUE

    @lm.noCallback
    async def header(self, key, val, cmdDict):
        """
        This gets one header from the email at a time.  The "key" is the
        LHS of the header and the "val" is RHS.
        ex.: key="Subject" , val="The subject of my email"

        str:key         The header name
        str:val         The header value
        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('%s: %s' % (key, val))
        return lm.CONTINUE

    @lm.noCallback
    async def eoh(self, cmdDict):
        """
        This tells you when all the headers have been received

        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('EOH')
        return lm.CONTINUE

    @lm.noCallback
    async def data(self, cmdDict):
        """
        This is called when the client sends DATA

        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('DATA')
        return lm.CONTINUE

    @lm.noCallback
    async def body(self, chunk, cmdDict):
        """
        This gets a chunk of the body of the email from the MTA.
        This will be called many times for a large email

        str:chunk       A chunk of the email's body
        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('Body chunk: %d' % len(chunk))
        return lm.CONTINUE

    async def eob(self, cmdDict):
        """
        This signals that the MTA has sent the entire body of the email.
        This is the callback where you can use modification methods,
        such as addHeader(), delRcpt(), etc.  If you return CONTINUE
        from this method, it will be the same as an returning ACCEPT.

        dict:cmdDict    The raw dictionary of items sent by the MTA

        Override this in a subclass.
        """
        self.log('Body finished')
        return lm.CONTINUE

    async def close(self):
        """
        Here, you can close any open resources.
        NOTE: this method is ALWAYS called when everything is complete.
        """
        self.log('Close called.  QID: %s' % self._qid)

    async def abort(self):
        """
        This is called when an ABORT is received from the MTA.
        NOTE: Postfix will send an ABORT at the end of every message.
        """
        pass

    @lm.noCallback
    async def unknown(self, cmdDict, data):
        return lm.CONTINUE
    # }}}

    #
    # Twisted method implementations {{{
    #
    async def connectionLost(self, reason=None):
        """
        The connection is lost, so we call the close method if it hasn't
        already been called
        """
        await self._close()

    async def dataReceived(self, buf):
        """
        This is the raw data receiver that calls the appropriate
        callbacks based on what is received from the MTA
        """
        remaining = 0
        cmds = []
        pheader = ''
        lm.debug('raw buf: %r' % buf, 4, self.id)
        if self._partialHeader:
            pheader = self._partialHeader
            lm.debug('Working a partial header: %r ; cmds: %r' % (pheader, cmds), 4, self.id)
            buf = pheader + buf
            self._partialHeader = None
        if self._partial:
            remaining, pcmds = self._partial
            self._partial = None
            buflen = len(buf)
            pcmds[-1] += buf[:remaining]
            buf = buf[remaining:]
            cmds.extend(pcmds)
            lm.debug('Got a chunk of a partial: len: %d ; ' % buflen +
                     'end of prev buf: %r ; ' % cmds[-1][-10:] +
                     'start of new buf: %r ; ' % buf[:10] +
                     'qid: %s ; ' % self._qid, 4, self.id)
            if buflen < remaining:
                remaining -= buflen
                self._partial = (remaining, cmds)
                return
            remaining = 0
        if buf:
            curcmds = []
            try:
                curcmds, remaining = lm.parse_packet(buf)
            except lm.InvalidPacket as e:
                lm.debug('Found a partial header: %r; cmdlen: %d ; buf: %r' %
                         (e.pp, len(e.cmds), buf), 2, self.id)
                cmds.extend(e.cmds)
                self._partialHeader = e.pp
            else:
                cmds.extend(curcmds)
        lm.debug('parsed packet, %d cmds , %d remaining: cmds: %r ; qid: %s' %
                 (len(cmds), remaining, cmds, self._qid), 2, self.id)
        if remaining:
            self._partial = (remaining, cmds[-1:])
            cmds = cmds[:-1]
        if cmds:
            await self._procCmdAndData(cmds)
    # }}}
