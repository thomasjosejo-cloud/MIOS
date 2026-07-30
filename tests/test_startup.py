"""Tests for application startup, shutdown, and dependency wiring."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from mios.cache import cache, get_cache
from mios.config import Settings, get_settings
from mios.core.startup import (
    StartupError,
    connect_infrastructure,
    disconnect_infrastructure,
)
from mios.db import database, get_session
from mios.db.session import Database
from mios.events import event_bus, get_jetstream


async def test_connect_infrastructure_connects_all_components(
    healthy_infrastructure: None, settings: Settings
) -> None:
    await connect_infrastructure(settings)

    assert isinstance(event_bus.connect, AsyncMock)
    event_bus.connect.assert_awaited_once()


@pytest.mark.parametrize("failing", ["database", "redis", "nats"])
async def test_startup_fails_fast_when_component_is_unavailable(
    healthy_infrastructure: None,
    monkeypatch: pytest.MonkeyPatch,
    failing: str,
) -> None:
    components = {"database": database, "redis": cache, "nats": event_bus}
    monkeypatch.setattr(components[failing], "ping", AsyncMock(return_value=False))
    settings = get_settings().model_copy(update={"STARTUP_VALIDATION": True})

    with pytest.raises(StartupError, match=failing):
        await connect_infrastructure(settings)


async def test_startup_tolerates_unavailable_components_when_validation_is_off(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setattr(database, "ping", AsyncMock(return_value=False))

    await connect_infrastructure(settings)


async def test_startup_reports_nats_connection_failure(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        event_bus, "connect", AsyncMock(side_effect=OSError("no servers available"))
    )
    monkeypatch.setattr(event_bus, "ping", AsyncMock(return_value=False))
    settings = get_settings().model_copy(update={"STARTUP_VALIDATION": True})

    with pytest.raises(StartupError, match="nats"):
        await connect_infrastructure(settings)


async def test_timescaledb_validation_is_skipped_when_disabled(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    verify = AsyncMock()
    monkeypatch.setattr("mios.core.startup.verify_timescaledb", verify)

    await connect_infrastructure(settings)

    verify.assert_not_awaited()


async def test_timescaledb_failure_aborts_startup(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    # `connect` is stubbed out, so stand in for the engine the check receives.
    monkeypatch.setattr(Database, "engine", MagicMock())
    monkeypatch.setattr(
        "mios.core.startup.verify_timescaledb",
        AsyncMock(side_effect=RuntimeError("extension not available")),
    )
    settings = get_settings().model_copy(
        update={"STARTUP_VALIDATION": True, "TIMESCALEDB_ENABLED": True}
    )

    with pytest.raises(StartupError, match="extension not available"):
        await connect_infrastructure(settings)


async def test_disconnect_tolerates_failures(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        database, "disconnect", AsyncMock(side_effect=OSError("already closed"))
    )

    await disconnect_infrastructure()

    assert isinstance(cache.disconnect, AsyncMock)
    cache.disconnect.assert_awaited_once()


def test_lifespan_releases_infrastructure_on_shutdown(
    healthy_infrastructure: None,
) -> None:
    from mios.main import app

    with TestClient(app):
        pass

    for component in (database, cache, event_bus):
        disconnect = component.disconnect
        assert isinstance(disconnect, AsyncMock)
        disconnect.assert_awaited()


def test_lifespan_aborts_when_startup_validation_fails(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mios.main import app

    monkeypatch.setattr(database, "ping", AsyncMock(return_value=False))
    monkeypatch.setenv("STARTUP_VALIDATION", "true")
    get_settings.cache_clear()

    try:
        with pytest.raises(StartupError), TestClient(app):
            pass
    finally:
        monkeypatch.delenv("STARTUP_VALIDATION", raising=False)
        get_settings.cache_clear()


async def test_get_session_requires_a_connected_database() -> None:
    with pytest.raises(RuntimeError, match="not connected"):
        async for _ in get_session():
            pass


def test_get_cache_requires_a_connected_client() -> None:
    with pytest.raises(RuntimeError, match="not connected"):
        get_cache()


def test_get_jetstream_requires_a_connected_bus() -> None:
    with pytest.raises(RuntimeError, match="not connected"):
        get_jetstream()


def test_dependencies_return_the_shared_infrastructure(settings: Settings) -> None:
    database.connect(settings)
    cache.connect(settings)
    try:
        assert isinstance(get_cache(), Redis)
        assert get_session.__annotations__["return"] is not None
        assert database.engine is not None
    finally:
        cache._client = None
        cache._pool = None
        database._engine = None
        database._sessionmaker = None


async def test_session_dependency_yields_async_session(settings: Settings) -> None:
    database.connect(settings)
    try:
        agen = database.session()
        session = await anext(agen)
        assert isinstance(session, AsyncSession)
        await agen.aclose()
    finally:
        await database.disconnect()
