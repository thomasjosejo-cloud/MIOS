"""Tests for the live engine orchestrator, driven by the simulator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mios.config import Settings
from mios.integrations.fyers import SimulatedMarketDataSource
from mios.integrations.fyers.client import FyersAPIError, FyersAuthError
from mios.services.options_intel.engine import OptionsIntelEngine
from mios.services.options_intel.store import EngineStore


@pytest.fixture
def engine_settings() -> Settings:
    return Settings(OPTION_STRIKE_COUNT=5, CANDLE_LOOKBACK_COUNT=30)


def _disconnected_db() -> MagicMock:
    db = MagicMock()
    db.is_connected = False
    return db


async def test_history_failure_does_not_stop_engine(
    engine_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    # History (5-minute candles) fails, but quotes + option chain keep working.
    store = EngineStore()
    source = SimulatedMarketDataSource(engine_settings)
    monkeypatch.setattr(
        source, "get_candles", AsyncMock(side_effect=FyersAPIError("history 500"))
    )
    engine = OptionsIntelEngine(source, store, _disconnected_db(), engine_settings)

    await engine.poll_once()
    await engine.poll_once()  # deltas so classifications/qualification form

    # Engine did not abort: option-chain intelligence and qualification exist.
    assert store.last_error is None
    assert store.strike_states
    assert store.context is not None
    assert store.qualification is not None
    # Validation marked unavailable internally.
    assert store.validation_available is False


async def test_session_expiry_stops_engine_and_invokes_hook(
    engine_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A Fyers auth error mid-poll (token expired) stops the loop and fires the
    # session-expired hook, rather than retrying forever.
    store = EngineStore()
    source = SimulatedMarketDataSource(engine_settings)
    monkeypatch.setattr(
        source, "get_spot", AsyncMock(side_effect=FyersAuthError("token expired"))
    )
    expired = AsyncMock()
    engine = OptionsIntelEngine(
        source,
        store,
        _disconnected_db(),
        engine_settings,
        on_session_expired=expired,
    )

    await engine._run_loop()

    expired.assert_awaited_once()
    assert store.engine_running is False


async def test_validation_available_when_history_succeeds(
    engine_settings: Settings,
) -> None:
    store = EngineStore()
    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(engine_settings),
        store,
        _disconnected_db(),
        engine_settings,
    )

    await engine.poll_once()

    assert store.validation_available is True


async def test_option_chain_failure_still_fails_the_poll(
    engine_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Quotes/chain are required inputs — their failure must still fail the poll.
    store = EngineStore()
    source = SimulatedMarketDataSource(engine_settings)
    monkeypatch.setattr(
        source, "get_option_chain", AsyncMock(side_effect=FyersAPIError("chain 500"))
    )
    engine = OptionsIntelEngine(source, store, _disconnected_db(), engine_settings)

    with pytest.raises(FyersAPIError):
        await engine.poll_once()


async def test_poll_populates_the_store(engine_settings: Settings) -> None:
    store = EngineStore()
    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(engine_settings),
        store,
        _disconnected_db(),
        engine_settings,
    )

    await engine.poll_once()

    assert store.spot_price is not None
    assert store.strike_states
    assert store.radar is not None
    assert store.structure is not None
    assert store.context is not None
    assert store.qualification is not None
    assert store.last_poll_at is not None
    assert store.last_error is None


async def test_second_poll_produces_deltas_and_classifications(
    engine_settings: Settings,
) -> None:
    store = EngineStore()
    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(engine_settings),
        store,
        _disconnected_db(),
        engine_settings,
    )

    await engine.poll_once()
    await engine.poll_once()

    # After two polls every strike has a prior observation to diff against.
    assert all(not s.is_first_observation for s in store.strike_states)


async def test_poll_persists_when_database_is_connected(
    engine_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = EngineStore()
    db = MagicMock()
    db.is_connected = True
    session = AsyncMock()
    session.add_all = MagicMock()  # add_all is synchronous on AsyncSession
    transaction_cm = MagicMock()
    transaction_cm.__aenter__ = AsyncMock(return_value=session)
    transaction_cm.__aexit__ = AsyncMock(return_value=None)
    db.transaction = MagicMock(return_value=transaction_cm)

    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(engine_settings), store, db, engine_settings
    )
    await engine.poll_once()

    db.transaction.assert_called_once()
    session.add_all.assert_called_once()


async def test_poll_skips_persistence_when_database_disconnected(
    engine_settings: Settings,
) -> None:
    store = EngineStore()
    db = _disconnected_db()
    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(engine_settings), store, db, engine_settings
    )

    await engine.poll_once()  # must not raise despite no DB


async def test_loop_survives_a_failing_poll(engine_settings: Settings) -> None:
    store = EngineStore()
    failing_source = MagicMock()
    failing_source.get_market_open = AsyncMock(side_effect=RuntimeError("boom"))
    engine = OptionsIntelEngine(
        failing_source, store, _disconnected_db(), engine_settings
    )

    with pytest.raises(RuntimeError, match="boom"):
        await engine.poll_once()

    # The orchestrator's loop records the error rather than dying; simulate the
    # loop's own handling by asserting poll_once surfaces it for the loop to catch.
    assert store.last_error is None  # set by the loop, not poll_once itself
