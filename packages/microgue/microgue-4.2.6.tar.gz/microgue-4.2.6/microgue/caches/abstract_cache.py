import datetime
import json

import redis

from ..loggers.logger import Logger

logger = Logger()


class CacheConnectionFailed(Exception):
    pass


class AbstractCache:
    # internal use only
    _cache_client = None

    # extension required
    host = None

    # extension optional
    port = 6379
    prefix = None
    ttl = 900
    connection_timeout = 1
    connection_required = True

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)

        # share the cache client at the __class__ level
        if self.__class__._cache_client is None:
            try:
                logger.debug("connecting to redis", priority=3)
                logger.debug(f"host: {self.host}")
                logger.debug(f"port: {self.port}")
                self.__class__._cache_client = redis.StrictRedis(
                    host=self.host,
                    port=self.port,
                    socket_connect_timeout=self.connection_timeout,
                )
                self.__class__._cache_client.ping()
            except Exception as e:
                logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                if self.connection_required:
                    raise CacheConnectionFailed(str(e))
                else:
                    self.__class__._cache_client = None

    def _prefix_key(self, key):
        if self.prefix:
            return f"{self.prefix}-{key}"
        else:
            return key

    def get(self, key):
        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)
        value = self._cache_client.get(prefixed_key)

        logger.debug(f"{self.__class__.__name__}.get", priority=2)
        logger.debug(f"key: {prefixed_key}")

        try:
            return json.loads(value)
        except:  # noqa
            pass
        try:
            return value.decode("ascii")
        except:  # noqa
            pass

        return value

    def set(self, key, value, ttl=None):
        if not self._cache_client:
            return False

        value = value if type(value) is str else json.dumps(value)
        prefixed_key = self._prefix_key(key)
        ttl = ttl or self.ttl

        logger.debug(f"{self.__class__.__name__}.set", priority=2)
        logger.debug(f"key: {prefixed_key}")

        self._cache_client.set(prefixed_key, value, ex=ttl)

        return True

    def delete(self, key):
        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)

        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"key: {prefixed_key}")

        return bool(self._cache_client.delete(prefixed_key))

    def expires_at(self, key):
        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)
        expire_time = self._cache_client.ttl(prefixed_key)

        return str(datetime.timedelta(seconds=expire_time))

    def clear(self):
        if not self._cache_client:
            return False

        logger.debug(f"{self.__class__.__name__}.clear", priority=2)

        return bool(self._cache_client.flushdb())
