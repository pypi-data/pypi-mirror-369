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
# based on the ratelimit plugin in the postomaat project (https://gitlab.com/fumail/postomaat)
# developed by @ledgr
import time
from collections import defaultdict
from threading import Lock
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DeclarativeBase, sql_alchemy_version, SQL_ALCHEMY_V2
from .backendint import BackendInterface
from fuglu.extensions.redisext import RedisPooledConn, ENABLED as REDIS_AVAILABLE

STRATEGY = 'sliding-log'
BACKENDS = defaultdict(dict)

__all__ = ['STRATEGY', 'BACKENDS']


class MemoryBackend(BackendInterface):
    def __init__(self, backendconfig: str):
        super().__init__(backendconfig=backendconfig)
        self.memdict = defaultdict(list)
        self.lock = Lock()

    def check_count(self, eventname, timediff, inc: int):
        """record a event. Returns the current count"""
        # add new event here
        now = self.add(eventname, inc=inc)
        then = now-timediff
        # remove elements older than now minus
        # timedifference (when element was added)
        self.clear(eventname, then)
        count = self.count(eventname, inc=inc)
        return count

    def add(self, eventname, inc: int):
        """add a tick to the event and return its timestamp"""
        now = time.time()
        self.lock.acquire()
        self.memdict[eventname].append((now, inc))
        self.lock.release()
        return now

    def clear(self, eventname, abstime=None):
        """
        clear events before abstime in secs
        if abstime is not provided, clears the whole queue
        """
        if abstime is None:
            abstime = int(time.time())

        if eventname not in self.memdict:
            return

        self.lock.acquire()
        try:
            self.memdict[eventname] = [v for v in self.memdict[eventname] if v[0] > abstime]
        except IndexError:  # empty list, remove
            del self.memdict[eventname]

        self.lock.release()

    def count(self, eventname, inc: int):
        self.lock.acquire()
        try:
            count = sum([v[1] for v in self.memdict[eventname]])
        except KeyError:
            count = 0
        self.lock.release()
        return count

    def check_allowed(self, eventname, limit, timespan, increment):
        count = self.check_count(eventname, timespan, inc=increment)
        return count <= limit, count


BACKENDS[STRATEGY]['memory'] = MemoryBackend


if REDIS_AVAILABLE:
    class RedisBackend(BackendInterface):
        def __init__(self, backendconfig: str):
            super().__init__(backendconfig=backendconfig)
            self.redis_pool = RedisPooledConn(backendconfig)

        def count(self, eventname, timespan):
            now = time.time()
            then = now-timespan
            if then is None:
                then = int(time.time())

            redisconn = self.redis_pool.get_conn()
            pipe = redisconn.pipeline()
            pipe.zadd(eventname, {now: now})
            pipe.zremrangebyscore(eventname, '-inf', then)
            pipe.zcard(eventname)
            return pipe.execute()[2]

        def check_allowed(self, eventname, limit, timespan, increment):
            eventname = self._fix_eventname(eventname)
            if increment != 1:
                raise NotImplementedError(f"increment={increment} is not implemented, use another backend/strategy!")
            count = self.count(eventname, timespan)
            return count <= limit, count

    BACKENDS[STRATEGY]['redis'] = RedisBackend


if SQL_EXTENSION_ENABLED:
    from sqlalchemy import Column, Integer, Unicode, BigInteger, Index
    from sqlalchemy.sql import and_
    metadata = DeclarativeBase.metadata

    class Event(DeclarativeBase):
        __tablename__ = 'fuglu_ratelimit_rolling_window'
        eventid = Column(BigInteger, primary_key=True)
        eventname = Column(Unicode(255), nullable=False)
        occurence = Column(Integer, nullable=False)
        __table_args__ = (
            Index('idx_eventname_rolling', 'eventname'),
        )

    class SQLAlchemyBackend(BackendInterface):
        def __init__(self, backendconfig: str):
            super().__init__(backendconfig=backendconfig)
            self.session = get_session(backendconfig)
            metadata.create_all(bind=self.session.bind)

        def db_add(self, eventname, timestamp):
            event = Event()
            event.eventname = eventname
            event.occurence = int(timestamp)
            self.session.add(event)
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                self.session.commit()
            self.session.flush()

        def db_clear(self, eventname, abstime):
            self.session.query(Event).filter(
                and_(Event.eventname == eventname, Event.occurence < abstime)
            ).delete()
            if sql_alchemy_version == SQL_ALCHEMY_V2:
                self.session.commit()
            self.session.flush()

        def db_count(self, eventname):
            return self.session.query(Event).filter(Event.eventname == eventname).count()

        def count(self, eventname, timespan):
            now = time.time()
            then = now-timespan
            if then is None:
                then = int(time.time())

            self.db_add(eventname, now)
            self.db_clear(eventname, then)
            return self.db_count(eventname)

        def check_allowed(self, eventname, limit, timespan, increment):
            eventname = self._fix_eventname(eventname)
            count = self.count(eventname, timespan)
            return count <= limit, count

    BACKENDS[STRATEGY]['sqlalchemy'] = SQLAlchemyBackend
