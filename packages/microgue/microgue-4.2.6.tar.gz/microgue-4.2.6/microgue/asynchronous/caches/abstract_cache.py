import datetime
import json

import redis.asyncio as redis

from ...loggers.logger import Logger

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
        pass

    async def connect(self):
        try:
            self._cache_client = await redis.Redis(
                host=self.host,
                port=self.port,
                socket_connect_timeout=self.connection_timeout,
            )
            await self._cache_client.ping()
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.connect - error", priority=3)
            logger.error(f"host: {self.host}")
            logger.error(f"port: {self.port}")
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            if self.connection_required:
                raise CacheConnectionFailed(str(e))
            else:
                self._cache_client = None

    def _prefix_key(self, key):
        if self.prefix:
            return f"{self.prefix}-{key}"
        else:
            return key

    async def get(self, key):
        await self.connect()

        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)
        value = await self._cache_client.get(prefixed_key)

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

    async def set(self, key, value, ttl=None):
        await self.connect()

        if not self._cache_client:
            return False

        value = value if type(value) is str else json.dumps(value)
        prefixed_key = self._prefix_key(key)
        ttl = ttl or self.ttl

        logger.debug(f"{self.__class__.__name__}.set", priority=2)
        logger.debug(f"key: {prefixed_key}")

        await self._cache_client.set(prefixed_key, value, ex=ttl)

        return True

    async def delete(self, key):
        await self.connect()

        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)

        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"key: {prefixed_key}")

        return bool(await self._cache_client.delete(prefixed_key))

    async def expires_at(self, key):
        await self.connect()

        if not self._cache_client:
            return False

        prefixed_key = self._prefix_key(key)
        expire_time = await self._cache_client.ttl(prefixed_key)

        return str(datetime.timedelta(seconds=expire_time))

    async def clear(self):
        await self.connect()

        if not self._cache_client:
            return False

        logger.debug(f"{self.__class__.__name__}.clear", priority=2)
        return bool(await self._cache_client.flushdb())
