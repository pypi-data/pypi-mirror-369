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
import logging
import time
from unittest.mock import MagicMock

try:
    import redis
    from redis import StrictRedis
    from redis import __version__ as redisversion
    STATUS = f"redis installed, version: {redisversion}"
    ENABLED = True
except ImportError:
    STATUS = "redis not installed"
    ENABLED = False
    StrictRedis = MagicMock()
    redis = MagicMock()
    redisversion = 'n/a'


class RedisPooledConn(object):
    def __init__(self, redis_url: str = None, **args):
        self.logger = logging.getLogger('fuglu.extensions.redis.RedisPooledConn')
        if 'password' in args.keys() and args['password']:
            self.logger.warning(f'deprecated redis password config - include it in redis_conn URL')
        elif 'password' in args.keys() and not args['password']:
            del args['password']

        if 'retry_on_timeout' not in args.keys():
            args['retry_on_timeout'] = True
        if 'socket_keepalive' not in args.keys():
            args['socket_keepalive'] = True
        if 'health_check_interval' not in args.keys():
            args['health_check_interval'] = 10
        if 'socket_connect_timeout' not in args.keys():
            if 'socket_timeout' in args.keys():
                args['socket_connect_timeout'] = args['socket_timeout']
            else:
                args['socket_connect_timeout'] = 5
        if 'client_name' not in args.keys():
            args['client_name'] = f'fuglu'
        
        if not ENABLED:
            self.pool = None
        elif not redis_url:
            self.pool = None
        elif redis is None:
            self.pool = None
            self.logger.error('Redis python module not installed')
        elif '://' in redis_url:
            self.pool = redis.ConnectionPool(**args)
            self.pool = self.pool.from_url(redis_url)
        else:
            self.logger.warning(f'deprecated redis connection string {redis_url}')
            host, port, db = redis_url.split(':')
            self.pool = redis.ConnectionPool(host=host, port=port, db=int(db), **args)

    def get_conn(self) -> StrictRedis:
        if not ENABLED:
            raise Exception('cannot get connection, redis extension not enabled')
        return StrictRedis(connection_pool=self.pool)

    def check_connection(self) -> bool:
        if self.pool is None:
            return False
        else:
            redisconn = self.get_conn()
            return redisconn.ping()


class ExpiringCounter(object):
    """
    Implentation of a counter that automatically decreases over time.
    
    Implemented as a redis hash with data format:
    key: { timestamp1:count1, timestamp2:count2, ... }
    the count is the sum of all count values where timestamp is not in the past
    """

    def __init__(self, redis_pool: RedisPooledConn = None, ttl: int = 0, maxcount: int = 0):
        self.redis_pool = redis_pool or RedisPooledConn()
        self.ttl = ttl
        self.maxcount = maxcount

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

    def increase(self, key: str, value: int = 1):
        """
        Given the identifier, create a new entry for current time with given value.
        Args:
            key (str): identifier
            value (int): value to set (increase) for current key and timestamp

        Returns:
            (int): return the increased counter value

        """
        redisconn = self.redis_pool.get_conn()
        if self.maxcount > 0:
            try:  # only increase if value is not already very high
                values = redisconn.hgetall(key)
                if len(values) > self.maxcount:
                    redisconn.expire(key, self.ttl)
                    return len(values)
            except redis.exceptions.TimeoutError:
                return 0

        try:
            ts = int(time.time()) + self.ttl
            pipe = redisconn.pipeline()
            # increase the value of 'ts' by 'value' for hash 'key'
            pipe.hincrby(key, str(ts), value)  # returns the value of redis[key][ts], usually same as param value
            pipe.expire(key, self.ttl)  # returns None, this is a safety measure to avoid stale keys
            result = pipe.execute()
            return result[0]
        except redis.exceptions.TimeoutError:
            return 0

    def get_count(self, key: str, cleanup: bool = True) -> int:
        """
        Get value. This is the sum of the count values within the ttl value stored in the class.
        Args:
            key (str): identifier
            cleanup (bool): Remove stale keys

        Returns:
            (int) aggregated value
        """
        count = 0
        delkeys = []
        redisconn = self.redis_pool.get_conn()
        values = redisconn.hgetall(key)
        ts = int(time.time())
        for k, v in values.items():
            if self._to_int(k) > ts:  # only count current keys
                count += self._to_int(v)
            elif cleanup:  # mark stale keys for cleanup
                delkeys.append(k)

        if delkeys and len(delkeys) == len(values):
            # all keys are stale
            redisconn.delete(key)
        elif delkeys:
            redisconn.hdel(key, *delkeys)

        return count

    def cleanup(self) -> None:
        """
        Remove stale entries from redis database
        """
        ts = int(time.time())
        redisconn = self.redis_pool.get_conn()
        for key in redisconn.scan_iter(match='*'):
            delete = False
            values = redisconn.hgetall(key)
            if not values:
                delete = True
            else:
                delkeys = []
                for k, v in values.items():
                    if self._to_int(k) <= ts:
                        delkeys.append(k)
                if delkeys and len(delkeys) == len(values):
                    delete = True
                elif delkeys:
                    redisconn.hdel(key, *delkeys)
            if delete:
                redisconn.delete(key)
