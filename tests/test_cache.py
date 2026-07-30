"""Tests for Redis infrastructure."""

from unittest.mock import AsyncMock

import pytest

from mios.cache.client import Cache
from mios.config import Settings


@pytest.fixture
def redis_cache() -> Cache:
    return Cache()


def test_client_is_not_created_at_import(redis_cache: Cache) -> None:
    assert redis_cache.is_connected is False

    with pytest.raises(RuntimeError, match="not connected"):
        _ = redis_cache.client


def test_connect_applies_pool_configuration(
    redis_cache: Cache, settings: Settings
) -> None:
    redis_cache.connect(settings)

    pool = redis_cache.client.connection_pool
    assert redis_cache.is_connected is True
    assert pool.max_connections == settings.REDIS_MAX_CONNECTIONS
    assert pool.connection_kwargs["db"] == settings.REDIS_DB


def test_connect_is_idempotent(redis_cache: Cache, settings: Settings) -> None:
    redis_cache.connect(settings)
    client = redis_cache.client
    redis_cache.connect(settings)

    assert redis_cache.client is client


async def test_disconnect_releases_client(
    redis_cache: Cache, settings: Settings
) -> None:
    redis_cache.connect(settings)
    await redis_cache.disconnect()

    assert redis_cache.is_connected is False


async def test_disconnect_is_safe_when_never_connected(redis_cache: Cache) -> None:
    await redis_cache.disconnect()

    assert redis_cache.is_connected is False


async def test_ping_is_false_when_not_connected(redis_cache: Cache) -> None:
    assert await redis_cache.ping() is False


async def test_ping_is_true_when_reachable(
    redis_cache: Cache, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    redis_cache.connect(settings)
    monkeypatch.setattr(redis_cache.client, "ping", AsyncMock(return_value=True))

    assert await redis_cache.ping() is True


async def test_ping_is_false_when_connection_refused(
    redis_cache: Cache, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    redis_cache.connect(settings)
    monkeypatch.setattr(
        redis_cache.client, "ping", AsyncMock(side_effect=OSError("refused"))
    )

    assert await redis_cache.ping() is False
