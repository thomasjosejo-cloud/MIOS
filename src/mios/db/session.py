"""Async database engine and session lifecycle."""

from collections.abc import AsyncGenerator, AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mios.config import Settings, get_settings
from mios.core.logging import get_logger

logger = get_logger(__name__)


class Database:
    """Owns the async engine and session factory for the application.

    The engine is created once at startup and disposed at shutdown, so the
    connection pool is never built at import time.
    """

    def __init__(self) -> None:
        """Create an unconnected database handle."""
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Return the active engine, or fail if the database is not connected."""
        if self._engine is None:
            msg = "Database is not connected; call connect() during startup"
            raise RuntimeError(msg)
        return self._engine

    @property
    def is_connected(self) -> bool:
        """Whether the engine has been created."""
        return self._engine is not None

    def connect(self, settings: Settings | None = None) -> None:
        """Create the engine and session factory with the configured pool."""
        if self._engine is not None:
            return

        settings = settings or get_settings()
        self._engine = create_async_engine(
            settings.database_dsn,
            echo=settings.POSTGRES_ECHO,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
            pool_recycle=settings.POSTGRES_POOL_RECYCLE,
            pool_pre_ping=settings.POSTGRES_POOL_PRE_PING,
            connect_args={"connect_timeout": settings.POSTGRES_CONNECT_TIMEOUT},
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
        )
        logger.info(
            "Database engine created",
            extra={
                "host": settings.POSTGRES_HOST,
                "port": settings.POSTGRES_PORT,
                "database": settings.POSTGRES_DB,
                "pool_size": settings.POSTGRES_POOL_SIZE,
            },
        )

    async def disconnect(self) -> None:
        """Dispose the engine, closing all pooled connections."""
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None
        logger.info("Database disconnected")

    async def ping(self) -> bool:
        """Verify real connectivity by issuing `SELECT 1`."""
        if self._engine is None:
            return False

        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            logger.exception("Database ping failed")
            return False
        return True

    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Yield a session, rolling back if the caller raises."""
        if self._sessionmaker is None:
            msg = "Database is not connected; call connect() during startup"
            raise RuntimeError(msg)

        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


database = Database()


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped database session."""
    async for session in database.session():
        yield session
