"""Tests for NATS JetStream infrastructure."""

import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest
from nats.aio.client import Client

from mios.config import Settings
from mios.events.client import EventBus


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def nats_client() -> MagicMock:
    client = MagicMock()
    client.is_connected = True
    client.jetstream.return_value = MagicMock()
    client.flush = AsyncMock()
    client.drain = AsyncMock()
    client.close = AsyncMock()
    return client


def test_client_is_not_created_at_import(bus: EventBus) -> None:
    assert bus.is_connected is False

    with pytest.raises(RuntimeError, match="not connected"):
        _ = bus.client

    with pytest.raises(RuntimeError, match="not connected"):
        _ = bus.jetstream


async def test_connect_acquires_jetstream_context(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connect = AsyncMock(return_value=nats_client)
    monkeypatch.setattr("mios.events.client.nats.connect", connect)

    await bus.connect(settings)

    assert bus.is_connected is True
    assert bus.jetstream is nats_client.jetstream.return_value
    assert connect.await_args is not None
    kwargs = connect.await_args.kwargs
    assert kwargs["servers"] == settings.NATS_SERVERS
    assert kwargs["max_reconnect_attempts"] == settings.NATS_MAX_RECONNECT_ATTEMPTS
    assert kwargs["reconnect_time_wait"] == settings.NATS_RECONNECT_TIME_WAIT


async def test_connect_is_idempotent(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connect = AsyncMock(return_value=nats_client)
    monkeypatch.setattr("mios.events.client.nats.connect", connect)

    await bus.connect(settings)
    await bus.connect(settings)

    connect.assert_awaited_once()


async def test_connect_failure_propagates(
    bus: EventBus, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "mios.events.client.nats.connect",
        AsyncMock(side_effect=OSError("no servers available")),
    )

    with pytest.raises(OSError, match="no servers available"):
        await bus.connect(settings)

    assert bus.is_connected is False


async def test_connect_options_match_the_real_client_signature(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Guard against a mocked `connect` hiding an option nats-py does not accept."""
    connect = AsyncMock(return_value=nats_client)
    monkeypatch.setattr("mios.events.client.nats.connect", connect)

    await bus.connect(settings)

    assert connect.await_args is not None
    supported = inspect.signature(Client.connect).parameters
    unsupported = set(connect.await_args.kwargs) - set(supported)
    assert not unsupported


async def test_initial_connect_is_bounded_by_a_deadline(
    bus: EventBus, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def never_connects(**_: object) -> MagicMock:
        await asyncio.sleep(60)
        raise AssertionError("unreachable")

    monkeypatch.setattr("mios.events.client.nats.connect", never_connects)
    bounded = settings.model_copy(update={"NATS_CONNECT_TIMEOUT": 0.05})

    with pytest.raises(TimeoutError):
        await bus.connect(bounded)

    assert bus.is_connected is False


async def test_disconnect_drains_connection(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mios.events.client.nats.connect", AsyncMock(return_value=nats_client)
    )
    await bus.connect(settings)

    await bus.disconnect()

    nats_client.drain.assert_awaited_once()
    assert bus.is_connected is False


async def test_disconnect_closes_when_drain_fails(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nats_client.drain.side_effect = OSError("drain timeout")
    monkeypatch.setattr(
        "mios.events.client.nats.connect", AsyncMock(return_value=nats_client)
    )
    await bus.connect(settings)

    await bus.disconnect()

    nats_client.close.assert_awaited_once()
    assert bus.is_connected is False


async def test_disconnect_is_safe_when_never_connected(bus: EventBus) -> None:
    await bus.disconnect()

    assert bus.is_connected is False


async def test_ping_is_false_when_not_connected(bus: EventBus) -> None:
    assert await bus.ping() is False


async def test_ping_is_false_when_link_is_down(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mios.events.client.nats.connect", AsyncMock(return_value=nats_client)
    )
    await bus.connect(settings)
    nats_client.is_connected = False

    assert await bus.ping() is False


async def test_ping_is_false_when_flush_times_out(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nats_client.flush.side_effect = TimeoutError
    monkeypatch.setattr(
        "mios.events.client.nats.connect", AsyncMock(return_value=nats_client)
    )
    await bus.connect(settings)

    assert await bus.ping() is False


async def test_reconnect_callbacks_are_registered(
    bus: EventBus,
    settings: Settings,
    nats_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connect = AsyncMock(return_value=nats_client)
    monkeypatch.setattr("mios.events.client.nats.connect", connect)

    await bus.connect(settings)

    assert connect.await_args is not None
    kwargs = connect.await_args.kwargs
    for callback in ("error_cb", "disconnected_cb", "reconnected_cb", "closed_cb"):
        assert callable(kwargs[callback])

    # Callbacks must be awaitable without raising.
    await kwargs["error_cb"](OSError("boom"))
    await kwargs["disconnected_cb"]()
    await kwargs["reconnected_cb"]()
    await kwargs["closed_cb"]()
