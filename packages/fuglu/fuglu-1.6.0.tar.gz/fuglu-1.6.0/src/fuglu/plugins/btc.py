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
import os
import re
import logging
import sys
import typing as tp
import socket
from hashlib import sha256
import html
from fuglu.shared import ScannerPlugin, AppenderPlugin, DUNNO, REJECT, FileList, SuspectFilter, apply_template, get_outgoing_helo, Suspect
from fuglu.extensions.aioredisext import AIORedisMixin, ENABLED as REDIS_AVAILABLE, ExpiringCounter
from fuglu.stringencode import force_bString, force_uString
try:
    import six
    if sys.version_info >= (3, 12, 0): # https://github.com/dpkp/kafka-python/issues/2401#issuecomment-1760208950
        sys.modules['kafka.vendor.six.moves'] = six.moves
    import kafka
    KAFKA_AVAILABLE=True
except ImportError:
    KAFKA_AVAILABLE=False



# https://stackoverflow.com/questions/21683680/regex-to-match-bitcoin-addresses
#    an identifier of 26-35 alphanumeric characters
#    beginning with the number 1 or 3
#    random digits
#    uppercase
#    lowercase letters
#    with the exception that the uppercase letter O, uppercase letter I, lowercase letter l, and the number 0 are never used to prevent visual ambiguity.

rgx_btc = '[13][a-km-zA-HJ-NP-Z1-9]{25,39}'
rgx_segwit = 'bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{25,39}'
btcrgx = re.compile('(%s|%s)' % (rgx_btc, rgx_segwit))



class NetBackend(object):
    def __init__(self, udptarget, tcptargets, timeout):
        self.udptarget = self._parse_target(udptarget)
        if tcptargets:
            self.tcptargets = [self._parse_target(t) for t in tcptargets]
        else:
            self.tcptargets = []
        self.timeout = timeout
    
    
    @staticmethod
    def _parse_target(target:str) -> tp.Optional[tp.Tuple[str, int]]:
        if not target:
            return None
        host, port = target.split(':', 1)
        port = int(port)
        return host, port
    
    
    def _send_udp(self, data:str, target:tp.Tuple[str, int]) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.setblocking(False)
        sock.sendto(force_bString(data + '\n'), target)
        try:
            sock.close()
        except Exception:
            pass
    
    
    def _send_tcp(self, data:str, target:tp.Tuple[str, int]) -> bool:
        sent = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.setblocking(False)
        try:
            sock.connect(target)
            sock.sendall(force_bString(data + '\n'))
            sent = True
        finally:
            try:
                sock.close()
            except Exception:
                pass
        return sent
    
    
    def send(self, data:str) -> None:
        if self.udptarget is not None:
            self._send_udp(data, self.udptarget)
        for tcptarget in self.tcptargets:
            sent = self._send_tcp(data, tcptarget)
            if sent:
                break


class KafkaBackend(object):
    def __init__(self, bootstrap_servers:tp.List[str], topic:str, timeout:float, username:tp.Optional[str], password:tp.Optional[str]):
        self.logger = logging.getLogger(f'fuglu.plugin.btc.{self.__class__.__name__}')
        self.clientid = f'prod-fuglu-{self.__class__.__name__}-{get_outgoing_helo()}'
        self.bootstrap_servers = bootstrap_servers
        self.timeout = timeout
        self.username = username
        self.password = password
        self.producer = None
        self.topic = topic
    
    
    def _init_producer(self):
        self.producer = kafka.KafkaProducer(bootstrap_servers=self.bootstrap_servers, api_version=(0, 10, 1),
                                            client_id=self.clientid, request_timeout_ms=self.timeout * 1000,
                                            sasl_plain_username=self.username, sasl_plain_password=self.password)
    
    
    
    def send(self, btcaddr:str) -> int:
        if self.producer is None:
            self._init_producer()
        messagebytes = force_bString(btcaddr)
        try:
            self.producer.send(self.topic, value=messagebytes, key=messagebytes)
            return 1  # stay compatible to redis backend, return 1 as in "counter increased by 1"
        except Exception as e:
            self.logger.error(f'failed to send message: {e.__class__.__name__}: {str(e)}')
            self.producer = None
            return 0  # error case: counter did not get increased



class BTCMixin(AIORedisMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requiredvars.update({
            'timeout': {
                'default': '2',
                'description': 'redis/kafka/udp/tcp timeout in seconds'
            },
            'ttl': {
                'default': '10368000',
                'description': 'TTL in seconds, defaults to 120d',
            },
            'max_count': {
                'default': '1000',
                'description': 'do not increase counter beyond this value (for performance reasons)'
            },
            'btcblacklistfile': {
                'default': '/etc/fuglu/conf.d/btcextract_btcblacklist.txt',
                'description': 'path to file containing hashes that should not be reported/evaluated. One hash per line, comments start after #',
            },
            'maxsize': {
                'default': '128000',
                'description': 'maximum size of each text part in bytes. larger text parts will be skipped',
            },
            'udptarget': {
                'default': '',
                'description': 'server:port definition to send btc address to by UDP protocol',
            },
            'tcptargets': {
                'default': '',
                'description': 'comma separated list of server:port definitions to send btc address to by TCP protocol. By default will only send to first host, if send fails, fallback to next host.',
            },
            'kafkahosts': {
                'default': '',
                'description:': 'kafka bootstrap hosts: host1:port host2:port'
            },
            'kafkatopic': {
                'default': 'bitcoinaddr',
                'description': 'name of kafka topic'
            },
            'kafkausername': {
                'default': '',
                'description:': 'kafka sasl user name for this producer'
            },
            'kafkapassword': {
                'default': '',
                'description': 'kafka sals password for this producer'
            },
        })
        self.btcvalidator = BTCValidator()
        self.segwitvalidator = SegwitValidator()
        self.filter = SuspectFilter(None)
        self.backend_redis = None
        self.backend_net = None
        self.backend_kafka = None
        self.btcblacklist = None
    
    
    _re_ws = re.compile(r'\s')
    _re_ast = re.compile(r'\*')
    def get_decoded_textparts(self, suspect:Suspect) -> tp.List[str]:
        textparts = []
        for attObj in suspect.att_mgr.get_objectlist(level=1, include_parents=True):
            if attObj.content_fname_check(contenttype_start='text/') or attObj.content_fname_check(name_end=('.txt', '.html', '.htm')):
                decoded_payload = attObj.decoded_buffer_text
                if not decoded_payload: # pdf body
                    decoded_payload = force_uString(attObj.buffer)
                
                if not decoded_payload:
                    self.logger.debug(f'{suspect.id} no payload in attachment {attObj.filename}')
                    continue
                
                if attObj.content_fname_check(contenttype_contains='html') or attObj.content_fname_check(name_contains='.htm'):
                    # remove all newline characters and replace them by single space
                    decoded_payload = decoded_payload.replace('\n', ' ').replace('\r', '')
                    decoded_payload = self.filter.strip_text(decoded_payload, fugluid=suspect.id)
                
                try:
                    decoded_payload = html.unescape(decoded_payload)
                except Exception:
                    self.logger.debug(f'{suspect.id} failed to unescape html entities in attachment {attObj.filename}')
                
                textparts.append(decoded_payload)
                
                # remove all whitespaces - may cause FPs!
                decoded_payload_nowhite = self._re_ws.sub('', decoded_payload)
                textparts.append(decoded_payload_nowhite)
                
                # remove some special characters - may cause FPs!
                decoded_payload_nospecial = self._re_ast.sub('', decoded_payload)
                textparts.append(decoded_payload_nospecial)
            
            if attObj.content_fname_check(contenttype='multipart/alternative'):
                textparts.append(attObj.decoded_buffer_text)
        return textparts
    
    
    
    def validate(self, btcaddr:str) -> bool:
        if btcaddr.startswith('bc1'):
            isvalid = self.segwitvalidator.validate(btcaddr)
        else:
            isvalid = self.btcvalidator.validate(btcaddr)
        return isvalid
    
    
    
    def extract(self, suspect:Suspect, maxsize:int, debug:bool=True) -> tp.List[str]:
        self._init_btcblacklist()
        if self.btcblacklist:
            btcblacklist = self.btcblacklist.get_list()
        else:
            btcblacklist = []
        
        btcaddrs_tmp = []
        textparts = self.get_decoded_textparts(suspect)
        for content in textparts:
            csize = len(content)
            if csize > maxsize:
                self.logger.debug(f'{suspect.id} text part size skip, {csize} > {maxsize}')
                continue
            result = btcrgx.findall(content)
            result = list(set(result))
            btcaddrs_tmp.extend(result)
        btcaddrs_tmp = list(set(btcaddrs_tmp))
        
        btcaddrs = []
        for btcaddr in btcaddrs_tmp:
            if btcaddr in btcblacklist:
                self.logger.info(f'{suspect.id} blacklisted BTC address: {btcaddr}')
                continue
            if not self.validate(btcaddr):
                debug and self.logger.debug(f'{suspect.id} not a valid BTC address: {btcaddr}')
                if len(btcaddr) > 30:  # sometimes we get a few characters too much
                    btcaddrs_tmp.append(btcaddr[:-1])
                continue
            btcaddrs.append(btcaddr.strip())
        return btcaddrs
    
    
    def _init_backend_redis(self):
        """
        Init Redis backend if not yet setup.
        """
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn:
            ttl = self.config.getint(self.section, 'ttl')
            maxcount = self.config.getint(self.section, 'max_count')
            timeout = self.config.getint(self.section, 'timeout')
            self.backend_redis = ExpiringCounter(self.aioredisbackend, ttl, maxcount=maxcount, timeout=timeout)
    
    
    
    def _init_backend_net(self):
        if self.backend_net is not None:
            return
        udptarget = self.config.get(self.section, 'udptarget')
        tcptargets = self.config.get(self.section, 'tcptargets')
        timeout = self.config.getint(self.section, 'timeout')
        try:
            if tcptargets:
                tcptargetslist = [x.strip() for x in tcptargets.split(',')]
            else:
                tcptargetslist = []
            if udptarget or tcptargetslist:
                self.backend_net = NetBackend(udptarget, tcptargets, timeout)
        except ValueError:
            self.logger.critical(f'Invalid net target configuration. Check {udptarget} and {tcptargets}')
    
    
    
    def _init_backend_kafka(self):
        if self.backend_kafka is not None:
            return
        hosts = self.config.get(self.section, 'kafkahosts').split()
        if hosts:
            topic = self.config.get(self.section, 'kafkatopic')
            timeout = self.config.getint(self.section, 'timeout')
            username = self.config.get(self.section, 'kafkausername')
            password = self.config.get(self.section, 'kafkapassword')
            self.backend_kafka = KafkaBackend(hosts, topic, timeout, username, password)
    
    
    
    def _init_btcblacklist(self):
        if self.btcblacklist is None:
            filename = self.config.get(self.section, 'btcblacklistfile')
            if filename and os.path.exists(filename):
                self.btcblacklist = FileList(
                    filename=filename,
                    lowercase=True, additional_filters=[FileList.inline_comments_filter])
    
    
    
    async def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        ok = self.check_config()
        fc = FunkyConsole()
        
        if not REDIS_AVAILABLE:
            print('ERROR: redis python module not available - this plugin will do nothing')
            return False
        
        if ok:
            try:
                ok = self.btcvalidator.validate('17rr7Jux3iz2H9662djZYKcQVgwDMw55Rv')
                if not ok:
                    print('ERROR: Failed to validate valid BTC address')
                ok = self.segwitvalidator.validate('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4')
                if not ok:
                    print('ERROR: Failed to validate valid BTC (segwit) address')
            except Exception as e:
                print('ERROR: Failed to validate BTC addresses, ancient python version fuckup? %s' % str(e))
        
        if ok:
            filename = self.config.get(self.section, 'btcblacklistfile')
            if not filename:
                print('INFO: blacklist file not specified')
            elif not os.path.exists(filename):
                print('ERROR: blacklist file %s not found' % filename)
                ok = False
            else:
                self._init_btcblacklist()
                if self.btcblacklist is not None:
                    btclist = self.btcblacklist.get_list()
                    print('found %s blacklisted hashes' % len(btclist))
        
        if ok and self.config.get(self.section, 'redis_conn'):
            try:
                reply = await self.aioredisbackend.ping()
                if reply:
                    print(fc.strcolor("OK: ", "green"), "redis server replied to ping")
                else:
                    ok = False
                    print(fc.strcolor("ERROR: ", "red"), "redis server did not reply to ping")
            except Exception as e:
                ok = False
                print(fc.strcolor("ERROR: ", "red"), f" -> {str(e)}")
                import traceback
                traceback.print_exc()
        
        elif ok and not self.config.get(self.section, 'redis_conn'):
            print(fc.strcolor("INFO: ", "blue"), f"No redis config specified")
        
        if ok:
            try:
                self._init_backend_net()
            except Exception as e:
                print(fc.strcolor("ERROR: ", "red"), f"failed to init netbackend: {str(e)}")
                ok = False
        return ok
    

    async def _incr_all_btcaddr(self, suspect:Suspect, btcaddrs:tp.List[str]):
        for btcaddr in btcaddrs:
            try:
                await self.backend_redis.increase(btcaddr)
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to increase redis counter due to {e.__class__.__name__}: {str(e)}')


    async def report(self, suspect:Suspect) -> None:
        if not REDIS_AVAILABLE:
            return
        
        maxsize = self.config.getint(self.section, 'maxsize')
        btcaddrs = self.extract(suspect, maxsize)
        if btcaddrs:
            self._init_backend_redis()
            self._init_backend_net()
            self._init_backend_kafka()
            if self.backend_redis is not None:
                await self._incr_all_btcaddr(suspect, btcaddrs)
            if self.backend_net is not None:
                for btcaddr in btcaddrs:
                    self.backend_net.send(btcaddr)
            if self.backend_kafka is not None:
                for btcaddr in btcaddrs:
                    self.backend_kafka.send(btcaddr)



class BTCReport(BTCMixin, ScannerPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        #BTCMixin.__init__(self) # should not be needed, but for some reason it is.
        self.logger = self._logger()
    
    
    async def lint(self):
        return await BTCMixin.lint(self)
    
    
    
    async def examine(self, suspect:Suspect):
        await self.report(suspect)
        return DUNNO



class BTCReportAppender(BTCMixin, AppenderPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        #BTCMixin.__init__(self) # should not be needed, but for some reason it is.
        self.logger = self._logger()
    
    
    async def lint(self):
        return await BTCMixin.lint(self)
    
    
    async def process(self, suspect:Suspect, decision):
        await self.report(suspect)



class BTCCounter(BTCReport):
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.requiredvars.update({
            'headername': {
                'default': 'X-BTCLevel',
                'description': 'header name',
            },
            
            'rejectlevel': {
                'default': '0',
                'description': 'Return REJECT instead or DUNNO if BTCLevel is higher than this threshold. A value of 0 or lower will never REJECT.'
            },
            
            'rejectmessage': {
                'default': 'Abused BTC address detected: ${btcaddr}',
                'description': "reject message template if running in pre-queue mode and reject level is reached.",
            },
            
            'debug': {
                'default': 'False',
                'description': 'print debug output (extra verbose)',
            },
        })
    
    
    async def lint(self):
        return await BTCMixin.lint(self)


    async def _get_all_counts(self, suspect:Suspect, btcaddrs:tp.List[str], btcblacklist:tp.List[str]) -> tp.Dict[str,int]:
        counts = {}
        for btcaddr in btcaddrs:
            btcaddr = btcaddr.strip()
            if btcaddr in btcblacklist:
                self.logger.debug(f'{suspect.id} blacklisted BTC address: {btcaddr}')
                continue
            if not (self.btcvalidator.validate(btcaddr) or self.segwitvalidator.validate(btcaddr)):
                self.logger.debug(f'{suspect.id} not a valid BTC address: {btcaddr}')
                continue
            counts[btcaddr] = await self.backend_redis.get_count(btcaddr)
        return counts
    
    
    async def _get_count(self, suspect:Suspect, btcaddrs:tp.List[str], btcblacklist:tp.List[str]) -> tp.Tuple[int,str|None]:
        level = -2
        btcaddr_hi = None
        self._init_backend_redis()
        if self.backend_redis is not None:
            try:
                btccount = await self._get_all_counts(suspect, btcaddrs, btcblacklist)
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to get data from redis due to {e.__class__.__name__}: {str(e)}')
                return -1, btcaddr_hi

            for btcaddr in btccount:
                btclvl = btccount[btcaddr]
                if btclvl > 0:
                    self.logger.info(f'{suspect.id} found BTC address {btcaddr} with count {btclvl}')
                elif btclvl == 0:
                    self.logger.debug(f'{suspect.id} BTC address {btcaddr} not found in database')
                elif btclvl < 0:
                    self.logger.debug(f'{suspect.id} BTC address {btcaddr} lookup error')
                if btclvl > 0 and (level is None or btclvl > level):
                    level = btclvl
                    btcaddr_hi = btcaddr
        return level, btcaddr_hi
    
    
    async def examine(self, suspect:Suspect):
        if not REDIS_AVAILABLE:
            return DUNNO
        
        level = -3
        btcaddr_hi = None
        maxsize = self.config.getint(self.section, 'maxsize')
        debug = self.config.getboolean(self.section, 'debug')
        btcaddrs = self.extract(suspect, maxsize, debug)
        if btcaddrs:
            self._init_btcblacklist()
            if self.btcblacklist:
                btcblacklist = self.btcblacklist.get_list()
            else:
                btcblacklist = []
            
            level, btcaddr_hi = await self._get_count(suspect, btcaddrs, btcblacklist)
        
        if btcaddr_hi is not None:
            suspect.set_tag('BTCAddr', btcaddr_hi)
        elif btcaddrs:
            suspect.set_tag('BTCAddr', btcaddrs[0])
        else:
            self.logger.debug(f'{suspect.id} no BTC addr found')
        
        if level > 0:
            suspect.set_tag('BTCLevel', level)
            headername = self.config.get(self.section, 'headername')
            suspect.write_sa_temp_header(headername, str(level))
        
        action = DUNNO
        message = None
        rejectlevel = self.config.getint(self.section, 'rejectlevel')
        if 0 < rejectlevel < level:
            action = REJECT
            values = dict(btcaddr=btcaddr_hi)
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
        
        return action, message




class BTCValidator(object):
    # based on https://github.com/nederhoed/python-bitcoinaddress/blob/master/bitcoinaddress/validation.py
    digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(f'fuglu.plugin.btc.{self.__class__.__name__}')
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = logger
    
    @staticmethod
    def _sha256(value:bytes) -> bytes:
        if sys.version_info < (2, 7):
            value = str(value)
        digest = sha256(value).digest()
        return digest
    
    def decode_base58(self, bitcoin_address:str, length:int) -> bytes:
        """Decode a base58 encoded address

        This form of base58 decoding is bitcoind specific. Be careful outside of
        bitcoind context.
        """
        n = 0
        for char in bitcoin_address:
            try:
                n = n * 58 + self.digits58.index(char)
            except Exception:
                msg = f'Character not part of Bitcoin\'s base58: {char}'
                raise ValueError(msg)
        return n.to_bytes(length, 'big')
    
    def encode_base58(self, bytestring:bytes) -> str:
        """Encode a bytestring to a base58 encoded string
        """
        # Count zero's
        zeros = 0
        for i in range(len(bytestring)):
            if bytestring[i] == 0:
                zeros += 1
            else:
                break
        n = int.from_bytes(bytestring, 'big')
        result = ''
        (n, rest) = divmod(n, 58)
        while n or rest:
            result += self.digits58[rest]
            (n, rest) = divmod(n, 58)
        return zeros * '1' + result[::-1]  # reverse string
    
    def validate(self, bitcoin_address:str, magicbyte:tp.Tuple[int,int]=(0, 5)) -> bool:
        """Check the integrity of a bitcoin address

        Returns False if the address is invalid.
        > self.validate('1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i')
        True
        > self.validate('')
        False
        """
        if isinstance(magicbyte, int):
            magicbyte = (magicbyte,)
        clen = len(bitcoin_address)
        if clen < 27 or clen > 35:  # XXX or 34?
            self.logger.debug(f'{bitcoin_address} invalid size {clen}')
            return False
        #allowed_first = tuple(string.digits)
        try:
            bcbytes = self.decode_base58(bitcoin_address, 25)
        except (ValueError, OverflowError):
            self.logger.debug(f'{bitcoin_address} invalid base58')
            return False
        # Check magic byte (for other altcoins, fix by Frederico Reiven)
        if magicbyte is not None:
            for mb in magicbyte:
                if bcbytes.startswith(chr(int(mb)).encode()):
                    break
            else:
                self.logger.debug(f'{bitcoin_address} invalid magic byte')
                return False
        # Compare checksum
        
        innerhash = self._sha256(bcbytes[:-4])
        checksum = self._sha256(innerhash)[:4]
        if bcbytes[-4:] != checksum:
            self.logger.debug(f'{bitcoin_address} invalid checksum')
            return False
        # Encoded bytestring should be equal to the original address,
        # for example '14oLvT2' has a valid checksum, but is not a valid btc
        # address
        enc_bcbytes = self.encode_base58(bcbytes)
        match = bitcoin_address == enc_bcbytes
        if not match:
            self.logger.debug(f'{bitcoin_address} not equals {enc_bcbytes}')
        return match



class SegwitValidator(object):
    # stolen from https://github.com/sipa/bech32/blob/master/ref/python/segwit_addr.py
    
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    
    @staticmethod
    def bech32_polymod(values:tp.List[int]) -> int:
        """Internal function that computes the Bech32 checksum."""
        generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for value in values:
            top = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ value
            for i in range(5):
                chk ^= generator[i] if ((top >> i) & 1) else 0
        return chk
    
    
    @staticmethod
    def bech32_hrp_expand(hrp:str) -> tp.List[int]:
        """Expand the HRP into values for checksum computation."""
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
    
    
    def bech32_verify_checksum(self, hrp:str, data:tp.List[int]) -> bool:
        """Verify a checksum given HRP and converted data characters."""
        return self.bech32_polymod(self.bech32_hrp_expand(hrp) + data) == 1
    
    
    def bech32_create_checksum(self, hrp:str, data:tp.List[int]) -> tp.List[int]:
        """Compute the checksum values given HRP and data."""
        values = self.bech32_hrp_expand(hrp) + data
        polymod = self.bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
        return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    
    
    def bech32_encode(self, hrp:str, data:tp.List[int]) -> str:
        """Compute a Bech32 string given HRP and data values."""
        combined = data + self.bech32_create_checksum(hrp, data)
        return hrp + '1' + ''.join([self.CHARSET[d] for d in combined])
    
    
    def bech32_decode(self, bech:str) -> tp.Tuple[tp.Optional[str], tp.Optional[tp.List[int]]]:
        """Validate a Bech32 string, and determine HRP and data."""
        if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
                (bech.lower() != bech and bech.upper() != bech)):
            return None, None
        bech = bech.lower()
        pos = bech.rfind('1')
        if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
            return None, None
        if not all(x in self.CHARSET for x in bech[pos + 1:]):
            return None, None
        hrp = bech[:pos]
        data = [self.CHARSET.find(x) for x in bech[pos + 1:]]
        if not self.bech32_verify_checksum(hrp, data):
            return None, None
        return hrp, data[:-6]
    
    
    @staticmethod
    def convertbits(data:tp.List[int], frombits:int, tobits:int, pad:bool=True) -> tp.Optional[tp.List[int]]:
        """General power-of-2 base conversion."""
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        max_acc = (1 << (frombits + tobits - 1)) - 1
        for value in data:
            if value < 0 or (value >> frombits):
                return None
            acc = ((acc << frombits) | value) & max_acc
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad:
            if bits:
                ret.append((acc << (tobits - bits)) & maxv)
        elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
            return None
        return ret
    
    
    
    def decode(self, hrp:str, addr:str) -> tp.Tuple[tp.Optional[int], tp.Optional[tp.List[int]]]:
        """Decode a segwit address."""
        hrpgot, data = self.bech32_decode(addr)
        if hrpgot != hrp:
            return None, None
        decoded = self.convertbits(data[1:], 5, 8, False)
        if decoded is None or len(decoded) < 2 or len(decoded) > 40:
            return None, None
        if data[0] > 16:
            return None, None
        if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
            return None, None
        return data[0], decoded
    
    
    
    def encode(self, hrp:str, witver:int, witprog:tp.List[int]) -> tp.Optional[str]:
        """Encode a segwit address."""
        ret = self.bech32_encode(hrp, [witver] + self.convertbits(witprog, 8, 5))
        if self.decode(hrp, ret) == (None, None):
            return None
        return ret
    
    
    @staticmethod
    def segwit_scriptpubkey(witver:int, witprog:tp.List[int]) -> bytes:
        """Construct a Segwit scriptPubKey for a given witness program."""
        return bytes([witver + 0x50 if witver else 0, len(witprog)] + witprog)
    
    
    
    def validate(self, address:str) -> bool:
        hrp = "bc"
        witver, witprog = self.decode(hrp, address)
        if witver is None:
            hrp = "tb"
            witver, witprog = self.decode(hrp, address)
        if witver is None:
            return False
        
        return True



if __name__ == '__main__':
    btcval = BTCValidator()
    valid = btcval.validate('1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i')
    print(valid)