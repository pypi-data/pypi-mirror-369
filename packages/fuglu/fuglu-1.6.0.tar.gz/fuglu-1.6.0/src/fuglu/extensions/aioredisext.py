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
import datetime
import asyncio
import time
from fuglu.stringencode import force_bString
from fuglu.asyncprocpool import get_event_loop
from typing import AsyncIterator, Optional, Dict, Union, List

try:
    import redis.asyncio as aioredis
    from redis import __version__ as redisversion
    STATUS = f"redis.asyncio installed, redis version: {redisversion}"
    ENABLED = True
    RETRY_ON_EXCS = (aioredis.ConnectionError,
                     aioredis.TimeoutError,
                     asyncio.exceptions.CancelledError,
                     asyncio.exceptions.TimeoutError,
                     )
except ImportError:
    STATUS = "redis.asyncio not installed"
    ENABLED = False
    aioredis = None
    redisversion = 'unkonwn'
    RETRY_ON_EXCS = (ConnectionError, TimeoutError)


AIOREDIS_TIMEOUT = 10.0
AIOEDIS_MAXATTEMPTS = 3
REDIS_POOL_TIMEOUT = 10
REDIS_POOL_MAXCON = 200
try:
    # linux only
    SOCKET_KEEPALIVE_OPTIONS = {
        socket.TCP_KEEPIDLE: 1,
        socket.TCP_KEEPCNT:  5,
        socket.TCP_KEEPINTVL: 3,
    }
except Exception:
    SOCKET_KEEPALIVE_OPTIONS = {}


class AIORedisBaseBackend:
    def __init__(self,
                 redis_url: str,
                 max_connections: int = REDIS_POOL_MAXCON,
                 socket_keepalive_options: Dict[int, int] = None,
                 socket_keepalive: bool = True,
                 retry_on_timeout: bool = False,
                 timeout: int = REDIS_POOL_TIMEOUT,
                 socket_timeout: float = REDIS_POOL_TIMEOUT,
                 socket_connect_timeout: float = REDIS_POOL_TIMEOUT,
                 logger: logging.Logger = None,
                 **kwargs):
        super().__init__()
        if logger is None:
            self.logger = logging.getLogger(f"fuglu.extensions.aioredis.{self.__class__.__name__}")
        else:
            self.logger = logger
        self._url = redis_url
        self._pool = self._create_pool(redis_url, max_connections, socket_keepalive_options,
                                       socket_keepalive, retry_on_timeout, timeout, socket_timeout,
                                       socket_connect_timeout, **kwargs)
        self._redis = None

    def _create_pool(self,
                     redis_url: str,
                     max_connections: int = REDIS_POOL_MAXCON,
                     socket_keepalive_options: Dict[int, int] = None,
                     socket_keepalive: bool = True,
                     retry_on_timeout: bool = False,
                     timeout: int = REDIS_POOL_TIMEOUT,
                     socket_timeout: float = REDIS_POOL_TIMEOUT,
                     socket_connect_timeout: float = REDIS_POOL_TIMEOUT,
                     **kwargs):

        if socket_keepalive_options is None:
            socket_keepalive_options = SOCKET_KEEPALIVE_OPTIONS

        pool = aioredis.BlockingConnectionPool(max_connections=max_connections,
                                               socket_keepalive_options=socket_keepalive_options,
                                               socket_keepalive=socket_keepalive,
                                               retry_on_timeout=retry_on_timeout,
                                               timeout=timeout,
                                               socket_timeout=socket_timeout,
                                               socket_connect_timeout=socket_connect_timeout,
                                               **kwargs).from_url(url=redis_url)
        return pool

    async def _get_redis(self):
        if self._redis is None:
            self.logger.debug(f"New redis instance connecting to pool(url={self._url})")
            self._redis = await aioredis.StrictRedis(connection_pool=self._pool)
        return self._redis

    async def get_redis(self, timeout_attempts: Optional[int] = None):
        if not self._redis:
            attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
            while attempts:
                attempts -= 1
                try:
                    await self._get_redis()
                except RETRY_ON_EXCS as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_redis' - retry ({typestring}: {str(e)})")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_redis' ({typestring}: {str(e)})")
                except Exception as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_redis' - retry ({typestring}: {str(e)})")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_redis': ({typestring}: {str(e)})", exc_info=e)

        return self._redis

    async def hgetall(self, key: bytes, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[Dict[bytes, bytes]]:
        keydata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    keydata = await r.hgetall(key)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hgetall' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hgetall' key={key} ({typestring}: {str(e)})")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hgetall' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hgetall' key={key} ({typestring}: {str(e)})", exc_info=e)
        return keydata

    async def hmget(self, key: bytes, fields: List[str], timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[List[bytes]]:
        keyfielddata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    keyfielddata = await r.hmget(name=key, keys=fields)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hmget' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hmget' key={key} ({typestring}: {str(e)})")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hmget' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hmget' key={key} ({typestring}: {str(e)})", exc_info=e)
        return keyfielddata

    async def get(self, key: bytes, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[List[bytes]]:
        keyfielddata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    keyfielddata = await r.get(name=key)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'get' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'get' key={key} ({typestring}: {str(e)})")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'get' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'get' key={key} ({typestring}: {str(e)})", exc_info=e)
        return keyfielddata

    async def delete(self, key: bytes, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[int]:
        keyfielddata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    keyfielddata = await r.delete(key)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'delete' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'delete' key={key} ({typestring}: {str(e)})")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'delete' key={key} - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'delete' key={key} ({typestring}: {str(e)})", exc_info=e)
        return keyfielddata

    async def scan_iter(self, match: str = "*", count: int = 250, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[AsyncIterator]:
        iterator = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                # iterator = await asyncio.wait_for(r.scan_iter(match=match, count=count), timeout=timeout)
                iterator = r.scan_iter(match=match, count=count)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'scan_iter' match={match} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'scan_iter' match={match} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'scan_iter' match={match} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'scan_iter' match={match} ({typestring}) {str(e)}", exc_info=e)
        if iterator:
            yield iterator

    async def hset(self, key: bytes, mapping: Dict, timeout: Optional[float] = None, ttl: Optional[Union[datetime.timedelta, int, float]] = None, timeout_attempts: Optional[int] = None) -> Optional[int]:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        # convert ttl to datetime object if required
        if isinstance(ttl, (int, float)):
            ttl = datetime.timedelta(seconds=ttl)

        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                pipe = await r.pipeline()
                pipe.hset(key, mapping=mapping)
                if ttl:
                    pipe.expire(key, time=ttl)
                async with asyncio.timeout(timeout):
                    reply = await pipe.execute()
                outdata = reply[0]
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hset' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hset' key={key} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hset' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hset' key={key} ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def hdel(self, key: bytes, mapping: List[bytes], timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[int]:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS

        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    outdata = await r.hdel(key, *mapping)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hdel' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hdel' key={key} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hdel' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hdel' key={key} ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def set(self, key: bytes, value: bytes, timeout: Optional[float] = None, ttl: Optional[Union[datetime.timedelta, int, float]] = None, timeout_attempts: Optional[int] = None) -> Optional[bool]:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        # convert ttl to datetime object if required
        if isinstance(ttl, (int, float)):
            ttl = datetime.timedelta(seconds=ttl)

        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                pipe = await r.pipeline()
                pipe.set(key, value)
                if ttl:
                    pipe.expire(key, time=ttl)
                async with asyncio.timeout(timeout):
                    reply = await pipe.execute()
                outdata = reply[0]
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'set' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'set' key={key} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'set' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'set' key={key} ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def hincrby(self, key: bytes, field: bytes, increment: Union[int, float] = 1, timeout: Optional[float] = None, ttl: Optional[Union[datetime.timedelta, int, float]] = None, timeout_attempts: Optional[int] = None) -> Optional[int]:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        # convert ttl to datetime object if required
        if isinstance(ttl, (int, float)):
            ttl = datetime.timedelta(seconds=ttl)
            
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                pipe = await r.pipeline()
                if isinstance(increment, int):
                    pipe.hincrby(key, field, amount=increment)
                else:
                    pipe.hincrbyfloat(key, field, amount=increment)
                if ttl:
                    pipe.expire(key, time=ttl)
                async with asyncio.timeout(timeout):
                    reply = await pipe.execute()
                outdata = reply[0]
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hincrby' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hincrby' key={key} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hincrby' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hincrby' key={key} ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def expire(self, key: Union[bytes, str], time: Union[int, datetime.datetime], timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> None:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis()
                async with asyncio.timeout(timeout):
                    outdata = await r.expire(key, time)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'expire' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'expire' key={key} ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'expire' key={key} - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'expire' key={key} ({typestring}) {str(e)}", exc_info=e)
        return outdata
    
    
    async def exists(self, key: Union[bytes, str], timeout: Optional[float] = None) -> bool:
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        r = await self._get_redis()
        async with asyncio.timeout(timeout):
            outdata = await r.exists(key)
        return outdata
    
    
    async def ttl(self, key: Union[bytes, str], timeout: Optional[float] = None) -> bool:
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        r = await self._get_redis()
        async with asyncio.timeout(timeout):
            outdata = await r.ttl(key)
        return outdata
    
    
    async def ping(self, timeout: Optional[float] = None) -> bool:
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        r = await self._get_redis()
        async with asyncio.timeout(timeout):
            outdata = await r.ping()
        return outdata

    async def close(self, timeout: Optional[float] = None):
        """Close open connections and pools"""
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        if self._redis:
            try:
                async with asyncio.timeout(timeout):
                    try:
                        await self._redis.aclose(close_connection_pool=False)
                    except AttributeError:
                        await self._redis.close(close_connection_pool=False)
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self.logger.warning(f"Problem closing redis connection: ({typestring}) {str(e)}")
            self._redis = None

        if self._pool:
            try:
                async with asyncio.timeout(timeout):
                    await self._pool.disconnect()
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self.logger.warning(f"Problem closing redis pool: ({typestring}) {str(e)}")
            self._pool = None

    def __del__(self):
        """destructor - make sure connections are all closed"""
        event_loop = get_event_loop(f'module=aioredis.destruct')
        try:
            if event_loop.is_running():
                event_loop.create_task(self.close(timeout=3.0))
            else:
                event_loop.run_until_complete(self.close(timeout=3.0))
        except Exception as e:
            typestring = str(type(e)).replace("<", "").replace(">", "")
            self.logger.warning(f"Problem closing redis pool: ({typestring}) {str(e)}")
    
class AIORedisMixin:
    """
    AsyncIO Redis Mixin class for Plugins
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requiredvars.update({
            'redis_conn': {
                'default': '',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },
        })
        
        self._aioredisbackend = None
        
    @property
    def aioredisbackend(self) -> AIORedisBaseBackend:
        if self._aioredisbackend is None:
            redis_url = self.config.get(self.section, 'redis_conn')
            self._aioredisbackend = AIORedisBaseBackend(redis_url=redis_url, logger=self.logger)
        return self._aioredisbackend


class ExpiringCounter:
    """
    Implentation of a counter that automatically decreases over time.

    Implemented as a redis hash with data format:
    key: { timestamp1:count1, timestamp2:count2, ... }
    the count is the sum of all count values where timestamp is not in the past
    """
    
    def __init__(self, aioredisbackend: AIORedisBaseBackend, ttl: int = 0, maxcount: int = 0, timeout: int = 3):
        self.aioredisbackend = aioredisbackend
        self.ttl = ttl
        self.maxcount = maxcount
        self.timeout = timeout
    
    def _to_int(self, value, default: int = 0) -> int:
        """
        Convert to integer if possible

        Args:
            value (str,unicode,bytes): string containing integer
        Keyword Args:
            default (int): value to be returned for conversion errors

        Returns:
            (int) value from string or default value

        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = default
        return value
    
    async def increase(self, key: str, value: int = 1) -> int:
        """
        Given the identifier, create a new entry for current time with given value.
        Args:
            key (str): identifier
            value (int): value to set (increase) for current key and timestamp

        Returns:
            (int): return the increased counter value

        """
        if self.maxcount > 0:
            # only increase if value is not already very high
            values = await self.aioredisbackend.hgetall(force_bString(key), timeout=self.timeout)
            if values is not None and len(values) > self.maxcount:
                await self.aioredisbackend.expire(key, self.ttl, timeout=self.timeout)
                return len(values)
        
        ts = str(int(time.time()) + self.ttl)
        # increase the value of 'ts' by 'value' for hash 'key'
        result = await self.aioredisbackend.hincrby(force_bString(key), force_bString(ts), value, ttl=self.ttl, timeout=self.timeout)  # returns the value of redis[key][ts], usually same as param value
        return result
    
    async def get_count(self, key: str, cleanup: bool = True) -> int:
        """
        Get value. This is the sum of the count values within the ttl value stored in the class.
        Args:
            key (str): identifier
            cleanup (bool): Remove stale keys

        Returns:
            (int) aggregated value
        """
        count = -1
        delkeys = []
        values = await self.aioredisbackend.hgetall(force_bString(key), timeout=self.timeout)
        if values is not None:
            count = 0
            ts = int(time.time())
            for k, v in values.items():
                if self._to_int(k) > ts:  # only count current keys
                    count += self._to_int(v)
                elif cleanup:  # mark stale keys for cleanup
                    delkeys.append(k)
        
        if delkeys and values and len(delkeys) == len(values):
            # all keys are stale
            await self.aioredisbackend.delete(force_bString(key), timeout=self.timeout)
        elif delkeys:
            await self.aioredisbackend.hdel(force_bString(key), delkeys, timeout=self.timeout)
        
        return count
    
    async def reset(self, key: bytes) -> Optional[int]:
        """
        Reset (delete) count for given key.
        Return values: None -> error deleting from redis, 0 -> nothing to delete, 1 -> success, anything else is suspicious.
        """
        val = await self.aioredisbackend.delete(key, timeout=self.timeout)
        return val
    
    async def cleanup(self) -> None:
        """
        Remove stale entries from redis database
        """
        ts = int(time.time())
        async for key in self.aioredisbackend.scan_iter(match='*'):
            delete = False
            values = await self.aioredisbackend.hgetall(key)
            if values:
                delkeys = []
                for k, v in values.items():
                    if self._to_int(k) <= ts:
                        delkeys.append(k)
                if delkeys and len(delkeys) == len(values):
                    delete = True
                elif delkeys:
                    await self.aioredisbackend.hdel(key, delkeys)
            if values is not None:
                delete = True
            if delete:
                await self.aioredisbackend.delete(key)