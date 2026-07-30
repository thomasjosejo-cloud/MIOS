"""Tests for database infrastructure."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import QueuePool

from mios.config import Settings
from mios.config.constants import DB_NAMING_CONVENTION
from mios.db import Base, metadata
from mios.db.session import Database
from mios.db.timescale import verify_timescaledb


@pytest.fixture
def db() -> Database:
    return Database()


def test_engine_is_not_created_at_import(db: Database) -> None:
    assert db.is_connected is False

    with pytest.raises(RuntimeError, match="not connected"):
        _ = db.engine


def test_connect_applies_pool_configuration(db: Database, settings: Settings) -> None:
    db.connect(settings)

    pool = db.engine.pool

    assert db.is_connected is True
    assert isinstance(pool, QueuePool)
    assert pool.size() == settings.POSTGRES_POOL_SIZE
    assert str(db.engine.url).startswith("postgresql+psycopg://")


def test_connect_is_idempotent(db: Database, settings: Settings) -> None:
    db.connect(settings)
    engine = db.engine
    db.connect(settings)

    assert db.engine is engine


async def test_disconnect_disposes_engine(db: Database, settings: Settings) -> None:
    db.connect(settings)
    await db.disconnect()

    assert db.is_connected is False


async def test_disconnect_is_safe_when_never_connected(db: Database) -> None:
    await db.disconnect()

    assert db.is_connected is False


async def test_ping_is_false_when_not_connected(db: Database) -> None:
    assert await db.ping() is False


async def test_ping_is_false_when_connection_fails(
    db: Database, settings: Settings
) -> None:
    db.connect(settings)
    failing = MagicMock()
    failing.connect.side_effect = OSError("connection refused")
    db._engine = failing

    assert await db.ping() is False


async def test_session_requires_connection(db: Database) -> None:
    with pytest.raises(RuntimeError, match="not connected"):
        async for _ in db.session():
            pass


async def test_session_yields_and_rolls_back_on_error(
    db: Database, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = AsyncMock(spec=AsyncSession)
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=None)
    db.connect(settings)
    monkeypatch.setattr(db, "_sessionmaker", MagicMock(return_value=context))

    generator = db.session()
    assert await anext(generator) is session

    # FastAPI throws the request's exception into the dependency generator; a bare
    # `async for` body raise would abandon it without reaching the rollback.
    with pytest.raises(ValueError, match="boom"):
        await generator.athrow(ValueError("boom"))

    session.rollback.assert_awaited_once()


def test_metadata_uses_naming_convention() -> None:
    assert Base.metadata is metadata
    assert dict(metadata.naming_convention) == DB_NAMING_CONVENTION


def test_no_orm_models_are_declared() -> None:
    """Sprint 2 is infrastructure only; models arrive in a later sprint."""
    assert metadata.tables == {}


async def test_verify_timescaledb_reports_installed_version() -> None:
    engine, connection = _engine_returning(["2.17.2"])

    assert await verify_timescaledb(engine) == "2.17.2"
    assert connection.execute.await_count == 1


async def test_verify_timescaledb_warns_when_available_but_not_enabled() -> None:
    engine, _ = _engine_returning([None, "2.17.2"])

    assert await verify_timescaledb(engine) is None


async def test_verify_timescaledb_raises_when_unavailable() -> None:
    engine, _ = _engine_returning([None, None])

    with pytest.raises(RuntimeError, match="not available"):
        await verify_timescaledb(engine)


def _engine_returning(scalars: list[str | None]) -> tuple[MagicMock, AsyncMock]:
    """Build a mock engine whose queries return `scalars` in order."""
    results = []
    for value in scalars:
        result = MagicMock()
        result.scalar.return_value = value
        results.append(result)

    connection = AsyncMock()
    connection.execute.side_effect = results

    engine = MagicMock()
    engine.connect.return_value.__aenter__.return_value = connection
    engine.connect.return_value.__aexit__.return_value = None
    return engine, connection
