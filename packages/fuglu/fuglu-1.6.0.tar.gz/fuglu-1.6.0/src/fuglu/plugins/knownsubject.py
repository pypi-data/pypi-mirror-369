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
import re
import os
from fuglu.shared import ScannerPlugin, AppenderPlugin, DUNNO, DELETE, Suspect, FileList, get_outgoing_helo
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.aioredisext import AIORedisMixin, ENABLED as REDIS_AVAILABLE, ExpiringCounter
try:
    from domainmagic.util import unconfuse
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False

    def unconfuse(value):
        return value
try:
    import sys
    if sys.version_info >= (3, 12, 0): # https://github.com/dpkp/kafka-python/issues/2401#issuecomment-1760208950
        import six
        sys.modules['kafka.vendor.six.moves'] = six.moves
    import kafka
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


class KnownSubjectMixin(AIORedisMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requiredvars.update({
            'headername': {
                'default': 'X-KnownSubjectScore',
                'description': 'header name',
            },
            'ttl': {
                'default': str(14 * 24 * 3600),
                'description': 'TTL in seconds',
            },
            'timeout': {
                'default': '2',
                'description': 'redis/kafka timeout in seconds'
            },
            'max_count': {
                'default': '1000',
                'description': 'do not increase counter beyond this value (for performance reasons)'
            },
            'skiplist': {
                'default': '${confdir}/knownsubject_skiplist.txt',
                'description': 'path to skiplist file, contains one skippable subject per line'
            },
            'kafkahosts': {
                'default': '',
                'description:': 'kafka bootstrap hosts: host1:port host2:port'
            },
            'kafkatopic': {
                'default': 'knownsubject',
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
        self.backend_redis = None
        self.backend_kafka = None
        self.skiplist = None


    def _init_skiplist(self):
        if self.skiplist is None:
            filepath = self.config.get(self.section, 'skiplist')
            if filepath and os.path.exists(filepath):
                self.skiplist = FileList(filename=filepath, additional_filters=[self._normalise_subject])

    def _init_backend_redis(self):
        """
        Init Redis backend if not yet setup.
        """
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn and REDIS_AVAILABLE:
            ttl = self.config.getint(self.section, 'ttl')
            maxcount = self.config.getint(self.section, 'max_count')
            timeout = self.config.getint(self.section, 'timeout')
            self.backend_redis = ExpiringCounter(self.aioredisbackend, ttl, maxcount=maxcount, timeout=timeout)

    async def _insert_redis(self, suspect:Suspect, subject:str):
        self._init_backend_redis()
        if self.backend_redis:
            multiplicator = self.config.getint(self.section, 'multiplicator')
            val = await self.backend_redis.increase(subject, multiplicator)
            if val > 0:
                self.logger.info(f'{suspect.id} subject {subject} registered in redis (result={val})')
            else:
                self.logger.error(f'{suspect.id} failed to register subject in redis {subject}')

    def _init_backend_kafka(self):
        if self.backend_kafka is not None:
            return
        bootstrap_servers = self.config.getlist(self.section, 'kafkahosts')
        if bootstrap_servers and KAFKA_AVAILABLE:
            self.kafkatopic = self.config.get(self.section, 'kafkatopic')
            timeout = self.config.getint(self.section, 'timeout')
            username = self.config.get(self.section, 'kafkausername')
            password = self.config.get(self.section, 'kafkapassword')
            clientid = f'prod-fuglu-{self.__class__.__name__}-{get_outgoing_helo(self.config)}'
            self.backend_kafka = kafka.KafkaProducer(bootstrap_servers=bootstrap_servers, api_version=(0, 10, 1), client_id=clientid,
                                                     request_timeout_ms=timeout*1000, sasl_plain_username=username, sasl_plain_password=password)

    def _insert_kafka(self, suspect:Suspect, subject:str):
        if self.backend_kafka is None:
            self._init_backend_kafka()
        if self.backend_kafka:
            messagebytes = force_bString(subject)
            try:
                self.backend_kafka.send(self.kafkatopic, value=messagebytes, key=messagebytes)
                self.logger.info(f'{suspect.id} subject {subject} registered in kafka')
            except Exception as e:
                self.logger.error(f'{suspect.id} failed to send message {suspect}: {e.__class__.__name__} {str(e)}')
                self.producer = None

    def _normalise_subject(self, subject:str, to_addr:str|None=None) -> str:
        if not subject:
            return subject
        s = subject.lower()  # small caps only
        s = unconfuse(s)  # replace all non-ascii characters by their ascii lookalike

        if to_addr:
            to_addr = force_uString(to_addr.lower())
            to_addr_lhs, to_addr_dom = to_addr.rsplit('@', 1)
            repl_map = [
                (to_addr, 'E'),
                (to_addr_lhs, 'L'),
                (to_addr_dom, 'D'),
            ]
            if '.' in to_addr_lhs:
                # maybe handle cases with more than one . in lhs
                fn, ln = to_addr_lhs.split('.', 1)
                repl_map.append((fn, 'F'))
                repl_map.append((ln, 'S'))
            for k, v in repl_map:  # remove to_addr,  to_addr lhs and domain name from subject
                s = s.replace(k, v)

        s = re.sub(r'^((?:re|fwd?|aw|tr|sv|rv)\W?:?\s?)+', '',  s)  # strip re/fwd prefix
        s = re.sub(r"(?:^|\s|\b|\w)([0-9'.,-]{2,16})(?:\s|\b|\w|$)", 'N', s)  # replace all number groups
        s = re.sub(r'[0-9]', 'X', s)  # replace individual numbers
        s = re.sub(r'[^\x00-\x7F]', 'U', s)  # replace non-ascii chars. note: unconfuse has already replaced special
                                             # chars we care by an ascii representation
        s = re.sub(r'\W', '', s, flags=re.UNICODE)  # remove all whitespaces and punctuations
        s = s[:32]  # shorten to a maximum of 32 chars
        return s

    def _get_subject(self, suspect:Suspect) -> str:
        subject = suspect.get_header('subject', '')
        subject = suspect.decode_msg_header(subject, logid=suspect.id)
        subject = self._normalise_subject(subject, suspect.to_address)
        if subject.isupper():  # ignore subjects that only consist of placeholders
            return ''
        if len(subject) < 3:  # ignore too short subjects
            return ''
        self._init_skiplist()
        if self.skiplist and subject in self.skiplist.get_list():
            return ''
        return subject

    async def _lint_redis(self, fc):
        ok = True
        try:
            self._init_backend_redis()
            reply = await self.aioredisbackend.ping()
            if reply:
                print(fc.strcolor("OK: ", "green"), "redis server replied to ping")
            else:
                ok = False
                print(fc.strcolor("ERROR: ", "red"), "redis server did not reply to ping")
        except Exception as e:
            ok = False
            print(fc.strcolor("ERROR: ", "red"), f"failed to talk to redis server: {e.__class__.__name__} {str(e)}")
            import traceback
            traceback.print_exc()
        return ok

    def _lint_kafka(self, fc):
        ok = True
        try:
            self._init_backend_kafka()
        except kafka.errors.KafkaError as e:
            print(f'ERROR: failed to connect to kafka: {str(e)}')
            ok = False
        except Exception as e:
            print(f'ERROR: Error connecting to kafka: {e.__class__.__name__} {str(e)}')
            self.logger.exception(e)
            ok = False
        return ok

    async def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            print(fc.strcolor("ERROR: ", "red"), 'neither redis nor kafka python module not available - this plugin will do nothing')
            return False

        ok = self.check_config()
        if ok:
            self._init_skiplist()
            if self.skiplist is None:
                print(fc.strcolor("WARNING: ", "red"), "skiplist not initialised")
                ok = False

        redis_conn = self.config.get(self.section, 'redis_conn')
        kafkahosts = self.config.get(self.section, 'kafkahosts')
        if not redis_conn and not kafkahosts:
            print(fc.strcolor("WARNING: ", "red"), "neither redis nor kafka specified, this plugin will have no effect")

        if ok:
            if redis_conn:
                ok = await self._lint_redis(fc)

        if ok:
            if kafkahosts:
                ok = self._lint_kafka(fc)

        return ok


class KnownSubject(KnownSubjectMixin, ScannerPlugin):
    """
    Check if normalised subject is found in redis database
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()

    async def examine(self, suspect):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return DUNNO

        if not suspect.from_address:
            self.logger.debug(f'{suspect.id} skipping bounce message')
            return DUNNO

        suspect.set_tag('KnownSubjectRun', True)

        subject = self._get_subject(suspect)
        if not subject:
            self.logger.debug(f'{suspect.id} skipping empty normalised subject')
            return DUNNO

        suspect.set_tag('KnownSubject', subject)
        
        await self._run(suspect, subject)
        return DUNNO


    async def _run(self, suspect: Suspect, subject: str):
        attempts = 2
        while attempts:
            attempts -= 1
            self._init_backend_redis()
            if self.backend_redis is None:
                continue
            count = await self.backend_redis.get_count(subject)
            if count < 0:
                self.logger.error(f'{suspect.id} failed to register subject {subject}')
            elif count == 0:
                self.logger.debug(f'{suspect.id} subject {subject} seen 0 times')
                attempts = 0
            else:
                suspect.set_tag('KnownSubjectScore', count)
                headername = self.config.get(self.section, 'headername')
                suspect.write_sa_temp_header(headername, count)
                self.logger.info(f'{suspect.id} subject {subject} seen {count} times')
                attempts = 0

    async def lint(self):
        return await KnownSubjectMixin.lint(self)


class KnownSubjectAppender(KnownSubjectMixin, AppenderPlugin):
    """
    Learn normalised subject to redis or kafka. Training plugin for KnownSubject.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars.update({
            'multiplicator': {
                'default': '1',
                'description': 'how many times does each entry count. you may want to set a higher value for trap processors'
            },
            'reportall': {
                'default': '0',
                'description': 'True: report all mails. False: only report spam/virus'
            },
            'original_sender_header': {
                'default': 'X-Original-Sender',
                'description': 'add original sender in this header'
            },
        })

    async def process(self, suspect, decision):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return
        
        if decision == DELETE:
            self.logger.debug(f'{suspect.id} skipping message due to decision=DELETE')
            return
        
        if not suspect.from_address:
            original_sender_header = self.config.get(self.section, 'original_sender_header')
            if not original_sender_header and not suspect.get_header(original_sender_header):
                self.logger.debug(f'{suspect.id} skipping bounce message')
                return

        reportall = self.config.getboolean(self.section, 'reportall')
        if not reportall and not (suspect.is_spam() or suspect.is_virus()):
            self.logger.debug(f'{suspect.id} skipped: not spam or virus')
            return

        has_run = suspect.get_tag('KnownSubjectRun', False)
        if has_run:
            subject = suspect.get_tag('KnownSubject')
        else:
            subject = self._get_subject(suspect)
            if not subject:
                self.logger.debug(f'{suspect.id} skipping empty normalised subject')
                return

        if subject is not None:
            await self._insert_redis(suspect, subject)
            self._insert_kafka(suspect, subject)

        return

    async def lint(self):
        return await KnownSubjectMixin.lint(self)
