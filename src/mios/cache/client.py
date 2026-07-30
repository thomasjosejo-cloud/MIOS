"""Redis connection lifecycle.

Provides the client and its lifecycle only. Caching policy belongs to the
components that consume it.
"""

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from mios.config import Settings, get_settings
from mios.core.logging import get_logger

logger = get_logger(__name__)


class Cache:
    """Owns the async Redis client and its connection pool."""

    def __init__(self) -> None:
        """Create an unconnected cache handle."""
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None

    @property
    def client(self) -> Redis:
        """Return the active client, or fail if Redis is not connected."""
        if self._client is None:
            msg = "Redis is not connected; call connect() during startup"
            raise RuntimeError(msg)
        return self._client

    @property
    def is_connected(self) -> bool:
        """Whether the client has been created."""
        return self._client is not None

    def connect(self, settings: Settings | None = None) -> None:
        """Create the client and connection pool. Connections are made lazily."""
        if self._client is not None:
            return

        settings = settings or get_settings()
        self._pool = ConnectionPool.from_url(
            settings.redis_dsn,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)
        logger.info(
            "Redis client created",
            extra={
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
                "max_connections": settings.REDIS_MAX_CONNECTIONS,
            },
        )

    async def disconnect(self) -> None:
        """Close the client and release all pooled connections."""
        if self._client is None:
            return

        await self._client.aclose()
        if self._pool is not None:
            await self._pool.aclose()
        self._client = None
        self._pool = None
        logger.info("Redis disconnected")

    async def ping(self) -> bool:
        """Verify real connectivity with a `PING` command."""
        if self._client is None:
            return False

        try:
            await self._client.ping()
        except Exception:
            logger.exception("Redis ping failed")
            return False
        return True


cache = Cache()


def get_cache() -> Redis:
    """FastAPI dependency returning the shared Redis client."""
    return cache.client
