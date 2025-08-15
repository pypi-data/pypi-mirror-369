#!/usr/bin/python3
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
import time
import hashlib
import re
import logging
import socket
import os
import asyncio
from email import message_from_bytes
from fuglu.shared import ScannerPlugin, AppenderPlugin, SuspectFilter, DUNNO, ACCEPT, ALLCODES, FileList, get_outgoing_helo
from fuglu.extensions.aioredisext import AIORedisMixin, AIORedisBaseBackend, ENABLED as REDIS_AVAILABLE
from fuglu.lib.patchedemail import PatchedMessage
from fuglu.stringencode import force_bString

CONN_EXC = []
if REDIS_AVAILABLE:
    import redis.asyncio
    CONN_EXC.append(redis.asyncio.ConnectionError)

try:
    import six
    import sys
    if sys.version_info >= (3, 12, 0): # https://github.com/dpkp/kafka-python/issues/2401#issuecomment-1760208950
        sys.modules['kafka.vendor.six.moves'] = six.moves
    # requires kafka-python
    import kafka
    CONN_EXC.append(kafka.errors.KafkaError)
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
CONN_EXC = tuple(CONN_EXC)


class FuzorMixin(AIORedisMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = None
        self.requiredvars.update({
            'backend': {
                'default': 'redis',
                'description': 'storage backend to be used. currently supported: redis (check/report), kafka (report only)'
            },
            'hash_algo': {
                'default': 'sha1',
                'description': f'hash algorithm to be used, specify any hash supported by hashlib: {",".join(hashlib.algorithms_available)}'
            },
    
            'redis_conn': {
                'default': 'redis://localhost:6379/0',
                'description': 'redis config: redis://host:port/db',
            },
            
            'redis_ttl': {
                'default': str(7*24*3600),
                'description': 'hash redis ttl in seconds (default 604800 or one week)',
            },
    
            'kafkahosts': {
                'default': '',
                'description:': 'kafka bootstrap hosts: host1:port host2:port'
            },
            'kafkatopic': {
                'default': 'fuzorhash',
                'description': 'name of kafka topic'
            },
            'kafkausername': {
                'default': '',
                'description:': 'kafka sasl user name for this producer'
            },
            'kafkapassword': {
                'default': '',
                'description': 'kafka sasl password for this producer'
            },
    
            'maxsize': {
                'default': '600000',
                'description':
                    'maxsize in bytes, larger messages will be skipped'
            },
            'stripoversize': {
                'default': 'False',
                'description':
                    'Remove attachments and reduce text to "maxsize" so large mails can be processed'
            },
            'timeout': {
                'default': '2',
                'description': 'timeout in seconds'
            },
        })

    def _init_backend(self):
        backend = self.config.get(self.section, 'backend').lower()

        try:
            if backend == 'redis':
                self._init_backend_redis()
            elif backend == 'kafka':
                self._init_backend_kafka()
            else:
                raise BackendError(f'backend={backend}, error=invalid backend')
        except CONN_EXC as e:
            raise BackendError(f'backend={backend}, error={str(e)}')

    def _init_backend_redis(self):
        if self.backend is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn and REDIS_AVAILABLE:
            timeout = self.config.getint(self.section, 'timeout')
            ttl = self.config.getint(self.section, 'redis_ttl')
            self.backend = RedisBackend(self.aioredisbackend, ttl, timeout)

    def _init_backend_kafka(self):
        if self.backend is not None:
            return
        hosts = self.config.get(self.section, 'kafkahosts').split()
        topic = self.config.get(self.section, 'kafkatopic')
        username = self.config.get(self.section, 'kafkausername')
        password = self.config.get(self.section, 'kafkapassword')
        timeout = self.config.getint(self.section, 'timeout')
        self.backend = KafkaBackend(hosts, topic, timeout, username, password, self.config)

    async def lint(self):
        if not self.check_config():
            return False

        if self.config.getboolean(self.section, 'stripoversize'):
            maxsize = self.config.getint(self.section, 'maxsize')
            print("Stripping oversize messages (size > %u) to calculate a fuzor hash..." % maxsize)
        
        hash_algo = self.config.get(self.section, 'hash_algo')
        if not hash_algo in hashlib.algorithms_available:
            print(f'ERROR: invalid hash algorithm {hash_algo} - use one of {",".join(hashlib.algorithms_available)}')
            return False

        backend = self.config.get(self.section, 'backend').lower()
        if backend == 'redis':
            ok = await self._lint_redis()
            print('INFO: using redis backend')
        elif backend == 'kafka':
            ok = self._lint_kafka()
            print('INFO: using kafka backend')
        else:
            print(f'ERROR: invalid backend {backend}')
            ok = False
        return ok

    async def _lint_redis(self):
        ok = True
        if not REDIS_AVAILABLE:
            print('ERROR: redis extension not available. This plugin will do nothing.')
            return False
        
        password = self.config.get(self.section, 'redis_password', fallback=None) or None
        if password is not None:
            print('deprecatioin warning: obsolete redis_password configured, set via redis_conn')
            
        if ok:
            try:
                self._init_backend()
                reply = await self.backend.aioredisbackend.ping()
                if reply:
                    print('OK: redis server replied to ping')
                else:
                    ok = False
                    print('ERROR: redis server did not reply to ping')

            except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError) as e:
                ok = False
                print(f'ERROR: failed to talk to redis server: {str(e)}')

        return ok

    def _lint_kafka(self):
        ok = True
        if not KAFKA_AVAILABLE:
            print('ERROR: kafka module not available. This plugin will do nothing.')
            ok = False

        if ok:
            try:
                self._init_backend()
            except Exception as e:
                print('ERROR: failed to connect to kafka: %s' % str(e))

        return ok

    async def report(self, suspect):
        digest = None
        count = 0
        if not REDIS_AVAILABLE:
            return digest, count

        maxsize = self.config.getint(self.section, 'maxsize')
        if suspect.size > maxsize:
            if self.config.getboolean(self.section, 'stripoversize'):
                suspect.debug(f'Fuzor: message size={suspect.size} too big, stripping down to maxsize={maxsize}')
                self.logger.debug(f'{suspect.id} message size={suspect.size} too big, stripping down to maxsize={maxsize}')
                msgrep = message_from_bytes(
                    suspect.source_stripped_attachments(maxsize=maxsize),
                    _class=PatchedMessage
                )
            else:
                self.logger.debug(f'{suspect.id} message too big, {suspect.size} > {maxsize}')
                return digest, count
        else:
            msgrep = suspect.get_message_rep()
            
        hash_algo = self.config.get(self.section, 'hash_algo')
        fuhash = FuzorDigest(msgrep, hash_algo)

        try:
            self.logger.debug(f"{suspect.id} to={suspect.to_address} hash={fuhash.digest} usable_body={fuhash.bodytext_size} predigest={fuhash.predigest[:50]} subject={msgrep.get('Subject')}")
        except Exception:
            pass

        if fuhash.digest is not None:
            amount = len(suspect.recipients)
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    starttime = time.time()
                    self._init_backend()
                    inittime = time.time()
                    count = await self.backend.increase(fuhash.digest, amount)
                    counttime = time.time()
                    itime = inittime-starttime
                    ctime = counttime-inittime
                    self.logger.debug(f"{suspect.id} hash {fuhash.digest} seen {count-1} times before inittime={itime:.2f}s counttime={ctime:.2f}s")
                    attempts = 0
                except (socket.timeout, redis.exceptions.TimeoutError) as e:
                    msg = f'{suspect.id} failed increasing count due to {str(e)}'
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
                except BackendError as e:
                    msg = f'{suspect.id} failed to connect to backend: {str(e)}, resetting connection'
                    self.backend = None
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
                except CONN_EXC as e:
                    msg = f'{suspect.id} failed increasing count due to {str(e)}, resetting connection'
                    self.backend = None
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
        else:
            self.logger.debug(f"{suspect.id} not enough data for a digest")

        if fuhash.digest is not None:
            return fuhash.digest, count
        else:
            return None, 0


class FuzorReport(FuzorMixin, ScannerPlugin):
    """ Report all messages to the fuzor redis backend"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

    async def examine(self, suspect):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return DUNNO

        digest, count = await self.report(suspect)
        if digest is not None and suspect.get_tag('FuZor') is None:
            suspect.set_tag('FuZor', (digest, count))
            suspect.set_tag('fuzor.digest', digest)
            suspect.set_tag('fuzor.count', count)
        return DUNNO

    def lint(self):
        return FuzorMixin.lint(self)


class FuzorReportAppender(FuzorMixin, AppenderPlugin):
    """ Report all messages to the fuzor redis backend"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

    async def process(self, suspect, decision):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return

        if decision not in [DUNNO, ACCEPT]:
            self.logger.debug(f'{suspect.id} not increasing count decision {ALLCODES.get(decision)}')
            return

        digest, count = await self.report(suspect)
        if digest is not None and suspect.get_tag('FuZor') is None:
            suspect.set_tag('FuZor', (digest, count))
            suspect.set_tag('fuzor.digest', digest)
            suspect.set_tag('fuzor.count', count)
            if count>0:
                self.logger.debug(f'{suspect.id} increased fuzor count for digest {digest} to {count}')
            else:
                self.logger.warning(f'{suspect.id} failed to increase fuzor count for digest {digest}')

    async def lint(self):
        return await FuzorMixin.lint(self)


class FuzorCheck(FuzorMixin, ScannerPlugin):
    """Check messages against the redis database and write spamassassin pseudo-headers"""

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'headername': {
                'default': 'X-FuZor',
                'description': 'header name',
            },
            'ignorelist': {
                'default': '',
                'description': 'path to file containing fuzor sums which should not be considered. one hash per line',
            },
        })
        self.ignorelist = None

    def _init_ignorelist(self):
        if self.ignorelist is None:
            filename = self.config.get(self.section, 'ignorelist')
            if filename and os.path.exists(filename):
                self.ignorelist = FileList(
                    filename=filename,
                    lowercase=True, additional_filters=[FileList.inline_comments_filter])

    async def examine(self, suspect):
        if not REDIS_AVAILABLE:
            return DUNNO

        # self.logger.info("%s: FUZOR START"%suspect.id)
        # start=time.time()
        maxsize = self.config.getint(self.section, 'maxsize')
        if suspect.size > maxsize:

            if self.config.getboolean(self.section, 'stripoversize'):
                suspect.debug(f'Fuzor: message size={suspect.size} too big, stripping down to maxsize={maxsize}')
                self.logger.debug(f'{suspect.id} message size={suspect.size} too big, stripping down to maxsize={maxsize}')
                msgrep = message_from_bytes(
                    suspect.source_stripped_attachments(maxsize=maxsize),
                    _class=PatchedMessage
                )
            else:
                suspect.debug('Fuzor: message too big, not digesting')
                self.logger.debug(f'{suspect.id} message too big, {suspect.size} > {maxsize}')
                # self.logger.info("%s: FUZOR END (SIZE SKIP)"%suspect.id)
                return DUNNO
        else:
            msgrep = suspect.get_message_rep()
        hash_algo = self.config.get(self.section, 'hash_algo')
        # self.logger.info("%s: FUZOR PRE-HASH"%suspect.id)
        fuhash = FuzorDigest(msgrep, hash_algo)
        digest = fuhash.digest
        # self.logger.info("%s: FUZOR POST-HASH"%suspect.id)
        if digest is not None:
            suspect.debug(f'Fuzor digest {digest}')

            self._init_ignorelist()
            if self.ignorelist is not None:
                ignorelist = self.ignorelist.get_list()
                if digest in ignorelist:
                    self.logger.info(f'{suspect.id} ignoring fuzor hash {digest}')
                    return DUNNO

            count = 0
            attempts = 2
            while attempts:
                attempts -= 1
                # self.logger.info("%s: FUZOR INIT-BACKEND"%suspect.id)
                # self.logger.info("%s: FUZOR START-QUERY"%suspect.id)
                try:
                    self._init_backend()
                    count = await self.backend.get(digest)
                except redis.exceptions.TimeoutError as e:
                    msg = f"{suspect.id} failed getting count due to {str(e)}"
                    if attempts:
                        self.logger.warning(msg)
                    else:
                        self.logger.error(msg)
                        return DUNNO
                except BackendError as e:
                    msg = f'{suspect.id} failed to initialise backend: {str(e)}, resetting connection'
                    self.backend = None
                    if attempts:
                        self.logger.warning(msg)
                    else:
                        self.logger.error(msg)
                        return DUNNO
                except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError) as e:
                    msg = f'{suspect.id} failed getting count due to {str(e)}, resetting connection'
                    self.backend = None
                    if attempts:
                        self.logger.warning(msg)
                    else:
                        self.logger.error(msg)
                        return DUNNO

            # self.logger.info("%s: FUZOR END-QUERY"%suspect.id)
            headername = self.config.get(self.section, 'headername')
            # for now, we only write the count, later we might replace with LOW/HIGH
            # if count>self.config.getint(self.section,'highthreshold'):
            #     self._writeheader(suspect,headername,'HIGH')
            # elif count>self.config.getint(self.section,'lowthreshold'):
            #     self._writeheader(suspect,headername,'LOW')
            suspect.set_tag('FuZor', (digest, count))
            suspect.set_tag('fuzor.digest', digest)
            suspect.set_tag('fuzor.count', count)
            if count > 0:
                # self.logger.info("%s: FUZOR WRITE HEADER"%suspect.id)
                suspect.write_sa_temp_header(f"{headername}-ID", digest)
                suspect.write_sa_temp_header(f"{headername}-Lvl", count)
                self.logger.info(f"{suspect.id} digest {digest} seen {count} times")
            else:
                self.logger.debug(f"{suspect.id} digest {digest} not seen before")
        else:
            suspect.debug(f'{suspect.id} not enough data for a digest')

        # diff=time.time()-start
        # self.logger.info("%s: FUZOR END (NORMAL), time =
        # %.4f"%(suspect.id,diff))
        return DUNNO

    async def lint(self):
        ok = True
        backend = self.config.get(self.section, 'backend').lower()
        if backend == 'kafka':
            print('ERROR: kafka backend is only supported for reports')
            ok = False

        filename = self.config.get(self.section, 'ignorelist')
        if filename and not os.path.exists(filename):
            ok = False
            print('cannot find ignorelist file %s' % filename)

        if ok:
            ok = await FuzorMixin.lint(self)
        return ok


class FuzorPrint(ScannerPlugin):
    """Just print out the fuzor hash (for debugging) """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

    def examine(self, suspect):
        hash_algo = self.config.get(self.section, 'hash_algo')
        msg = suspect.get_message_rep()
        fuhash = FuzorDigest(msg, hash_algo)
        if fuhash.digest is not None:
            self.logger.info(f'{suspect.id} Predigest: {fuhash.predigest}')
            self.logger.info(f'{suspect.id} hash {fuhash.digest}')
        else:
            self.logger.info(f'{suspect.id} does not produce enough data for a unique hash')

        return DUNNO


class FuzorDigest(object):
    def __init__(self, msg, hash_algo):
        self.debug = []
        self.digest = None
        self.predigest = None
        self.bodytext_size = 0
        self.filter = SuspectFilter(None)
        self.logger = logging.getLogger('fuglu.plugin.fuzor.Digest')

        # digest config
        self.LONG_WORD_THRESHOLD = 10  # what is considered a long word
        self.REPLACE_LONG_WORD = '[LONG]'  # Replace long words in pre-digest with... None to disable
        self.REPLACE_EMAIL = '[EMAIL]'  # Replace email addrs in pre-digest with... None to disable
        self.REPLACE_URL = '[LINK]'  # Replace urls in pre-digest with... None to disable
        # should non-text attachment contents be included in digest (not recommended, there are better attachment hash systems)
        self.INCLUDE_ATTACHMENT_CONTENT = False
        self.INCLUDE_ATTACHMENT_COUNT = True  # should the number of non-text-attachments be included in the digest
        self.MINIMUM_PREDIGEST_SIZE = 27  # if the pre-digest is smaller than this, ignore this message
        # minimum unmodified content after stripping, eg. [SOMETHING] removed from the predigest (27>'von meinem Iphone gesendet')
        self.MINIMUM_UNMODIFIED_CONTENT = 27
        self.MINIMUM_BODYTEXT_SIZE = 27  # if the body text content is smaller than this, ignore this message
        self.STRIP_WHITESPACE = True  # remove all whitespace from the pre-digest
        self.STRIP_HTML_MARKUP = True  # remove html tags (but keep content)
        self.REMOVE_HTML_TAGS = [
            'script',
            'style',
        ]  # strip tags (including content)
        
        self.hasher = getattr(hashlib, hash_algo)
        self.predigest = self._make_predigest(msg)
        self.digest = self._make_hash(self.predigest)
    
    _re_hex = re.compile(r'\[[A-Z0-9:]{1,1024}]')
    def _make_hash(self, predigest):
        if self.bodytext_size < self.MINIMUM_BODYTEXT_SIZE:
            return None
        predigest = predigest.strip()
        if len(predigest) < self.MINIMUM_PREDIGEST_SIZE:
            return None
        unmodified = self._re_hex.sub('', predigest)
        if len(unmodified) < self.MINIMUM_UNMODIFIED_CONTENT:
            return None

        predigest = predigest.encode('utf-8', errors='ignore')
        return self.hasher(predigest).hexdigest()
    
    _re_email = re.compile(r'\S{1,50}@\S{1,30}')
    _re_uri = re.compile(r'[a-z]{1,1024}:\S{1,100}')
    _re_ws = re.compile(r'\s')
    def _handle_text_part(self, part):
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset()
        errors = "ignore"
        if not charset:
            charset = "ascii"
        elif charset.lower().replace("_", "-") in ("quopri-codec", "quopri", "quoted-printable", "quotedprintable"):
            errors = "strict"

        try:
            payload = payload.decode(charset, errors)
        except (LookupError, UnicodeError, AssertionError):
            payload = payload.decode("ascii", "ignore")

        if self.STRIP_HTML_MARKUP:
            payload = self.filter.strip_text(
                payload,
                remove_tags=self.REMOVE_HTML_TAGS,
                use_bfs=True)

        if self.REPLACE_EMAIL is not None:
            payload = self._re_email.sub(self.REPLACE_EMAIL, payload)

        if self.REPLACE_URL is not None:
            payload = self._re_uri.sub(self.REPLACE_URL, payload)

        if self.REPLACE_LONG_WORD is not None:
            patt = r'\S{%s,}' % self.LONG_WORD_THRESHOLD
            payload = re.sub(patt, self.REPLACE_LONG_WORD, payload)

        if self.STRIP_WHITESPACE:
            payload = self._re_ws.sub('', payload)
        payload = payload.strip()
        return payload

    def _make_predigest(self, msg):
        attachment_count = 0
        predigest = ''
        for part in msg.walk():
            if part.is_multipart():
                continue

            if part.get_content_maintype() == "text":
                try:
                    normalized_text_part = self._handle_text_part(part)
                    predigest += normalized_text_part
                    self.bodytext_size += len(normalized_text_part)
                except Exception as e:
                    self.logger.warning(e)
            else:
                attachment_count += 1
                if self.INCLUDE_ATTACHMENT_CONTENT:
                    predigest += f"[ATTH:{self.hasher(part.get_payload()).hexdigest()}]"

        if self.INCLUDE_ATTACHMENT_COUNT and attachment_count:
            predigest += f"[ATTC:{attachment_count}]"

        if self.STRIP_WHITESPACE:
            predigest = self._re_ws.sub('', predigest)

        return predigest


class BackendError(Exception):
    pass


class FuzorBackend:
    async def increase(self, digest, amount=1):
        raise NotImplementedError()

    async def get(self, digest):
        raise NotImplementedError()


class RedisBackend(FuzorBackend):
    def __init__(self, aioredisbackend: AIORedisBaseBackend, ttl:int, timeout:int):
        self.aioredisbackend = aioredisbackend
        self.ttl = ttl
        self.timeout = timeout
        self.logger = logging.getLogger("fuglu.plugin.fuzor.RedisBackend")

    async def increase(self, digest, amount=1):
        redisconn = await self.aioredisbackend._get_redis()
        pipe = await redisconn.pipeline()
        pipe.incr(digest, amount)
        pipe.expire(digest, self.ttl)
        async with asyncio.timeout(self.timeout):
            result = await pipe.execute()
        return result[0]

    async def get(self, digest):
        try:
            async with asyncio.timeout(self.timeout):
                value = await self.aioredisbackend.get(digest)
            return int(value)
        except (ValueError, TypeError):
            return 0
        except Exception as e:
            self.logger.info(f"failed to query fuzor redis due to {e.__class__.__name__}: {str(e)}")
            return 0


class KafkaBackend(FuzorBackend):
    def __init__(self, bootstrap_servers, topic, timeout, username, password, config=None):
        self.logger = logging.getLogger("fuglu.plugin.fuzor.KafkaBackend")
        clientid = 'prod-fuglu-%s-%s' % (self.__class__.__name__, get_outgoing_helo(config))
        self.producer = kafka.KafkaProducer(
            bootstrap_servers=bootstrap_servers, api_version=(0, 10, 1), client_id=clientid,
            request_timeout_ms=timeout*1000, sasl_plain_username=username, sasl_plain_password=password
        )
        self.topic = topic

    async def increase(self, digest, amount=1):
        messagebytes = force_bString(digest)
        for x in range(0, amount):
            self.producer.send(self.topic, value=messagebytes, key=messagebytes)
        return amount  # stay compatible to redis backend, return 1 as in "counter increased by 1"

    async def get(self, digest):
        raise BackendError('Kafka backend can only be used for reporting')


if __name__ == '__main__':
    import email
    import sys
    mymsg = email.message_from_file(sys.stdin)
    hash_algo = 'sha1'
    if len(sys.argv) > 1:
        hash_algo = sys.argv[1]
    mydigest = FuzorDigest(mymsg, hash_algo)
    print("Pre-digest: %s" % mydigest.predigest)
    print("Digest: %s" % mydigest.digest)
