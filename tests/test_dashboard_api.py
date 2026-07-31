"""Tests for the /dashboard aggregation endpoint."""

import datetime as dt
from collections.abc import Iterator
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mios.config import Settings
from mios.integrations.fyers import SimulatedMarketDataSource
from mios.schemas.dashboard import DashboardResponse
from mios.services.options_intel import runtime
from mios.services.options_intel.dashboard import build_dashboard
from mios.services.options_intel.engine import OptionsIntelEngine
from mios.services.options_intel.store import EngineStore


@pytest.fixture
def fresh_store(monkeypatch: pytest.MonkeyPatch) -> EngineStore:
    """Replace the process-wide store with an empty one for isolation."""
    store = EngineStore()
    monkeypatch.setattr(runtime, "store", store)
    return store


@pytest.fixture
def api(healthy_infrastructure: None, fresh_store: EngineStore) -> Iterator[TestClient]:
    """Test client sharing the fresh store the endpoint reads from."""
    from mios.main import app

    with TestClient(app) as client:
        yield client


def _seed(store: EngineStore) -> None:
    """Populate the store by driving two engine polls on the simulator."""
    import asyncio

    async def run() -> None:
        settings = Settings(OPTION_STRIKE_COUNT=5, CANDLE_LOOKBACK_COUNT=30)
        db = MagicMock()
        db.is_connected = False
        engine = OptionsIntelEngine(
            SimulatedMarketDataSource(settings), store, db, settings
        )
        store.engine_running = True
        await engine.poll_once()
        await engine.poll_once()

    asyncio.run(run())


# --- Endpoint & schema -------------------------------------------------------


def test_dashboard_returns_full_envelope(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    response = api.get("/api/v1/dashboard")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert set(body) == {
        "connection_state",
        "authentication",
        "data_source",
        "market",
        "narrative",
        "dominance",
        "qualification",
        "context",
        "ce_pe",
        "option_chain",
        "engine",
    }
    assert body["authentication"] in ("CONNECTED", "NOT_AUTHENTICATED")


def test_dashboard_matches_response_schema(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    body = api.get("/api/v1/dashboard").json()

    # Round-trips through the declared contract without error.
    parsed = DashboardResponse.model_validate(body)
    assert parsed.market.status in ("LIVE", "CLOSED")
    assert parsed.option_chain


def test_option_chain_trimmed_to_five_per_side(
    fresh_store: EngineStore,
) -> None:
    # Sprint 10.1: the chain shows at most 5 CE + 5 PE around the money, even
    # when the engine tracks many more strikes.
    import asyncio

    async def run() -> None:
        settings = Settings(OPTION_STRIKE_COUNT=21, CANDLE_LOOKBACK_COUNT=30)
        db = MagicMock()
        db.is_connected = False
        engine = OptionsIntelEngine(
            SimulatedMarketDataSource(settings), fresh_store, db, settings
        )
        fresh_store.engine_running = True
        await engine.poll_once()
        await engine.poll_once()

    asyncio.run(run())

    dashboard = build_dashboard(fresh_store)
    ce = [r for r in dashboard.option_chain if r.option_type.value == "CE"]
    pe = [r for r in dashboard.option_chain if r.option_type.value == "PE"]

    assert len(dashboard.option_chain) <= 10
    assert len(ce) <= 5
    assert len(pe) <= 5


def test_option_chain_rows_have_required_fields(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    rows = api.get("/api/v1/dashboard").json()["option_chain"]

    assert rows
    for row in rows:
        assert set(row) == {
            "strike",
            "option_type",
            "premium",
            "oi",
            "oi_change",
            "volume",
            "classification",
            "unusual_flags",
            "recommendation_flag",
        }
        assert isinstance(row["unusual_flags"], list)
        assert isinstance(row["recommendation_flag"], bool)


# --- Healthy engine ----------------------------------------------------------


def test_healthy_engine_reports_runtime_and_age(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    engine = api.get("/api/v1/dashboard").json()["engine"]

    assert engine["healthy"] is True
    assert engine["pipeline_runtime_ms"] is not None
    assert engine["pipeline_runtime_ms"] >= 0
    assert engine["data_age_seconds"] is not None
    assert engine["data_age_seconds"] >= 0


def test_spot_change_is_derived_from_previous_close(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    market = api.get("/api/v1/dashboard").json()["market"]

    # Change is measured against the feed's previous close (24650 in the
    # simulator), not the previous poll — so it reflects the day's move.
    assert market["spot"] is not None
    assert market["change"] is not None
    assert market["change_percent"] is not None
    expected_change = float(market["spot"]) - 24650.0
    assert float(market["change"]) == pytest.approx(expected_change, abs=0.01)


# --- Empty market ------------------------------------------------------------


def test_empty_market_returns_well_formed_envelope(api: TestClient) -> None:
    # No poll has run: the store is empty. The dashboard must still return 200
    # with a well-formed body rather than erroring.
    response = api.get("/api/v1/dashboard")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["market"]["spot"] is None
    assert body["market"]["change"] is None
    assert body["market"]["status"] == "CLOSED"
    assert body["qualification"] is None
    assert body["narrative"] is None
    assert body["dominance"] is None
    assert body["option_chain"] == []
    assert body["engine"]["healthy"] is False
    assert body["engine"]["data_age_seconds"] is None


# --- Market closed -----------------------------------------------------------


def test_market_closed_status(fresh_store: EngineStore) -> None:
    _seed(fresh_store)
    fresh_store.market_open = False

    dashboard = build_dashboard(fresh_store)

    assert dashboard.market.status == "CLOSED"


def test_market_live_status(fresh_store: EngineStore) -> None:
    _seed(fresh_store)
    fresh_store.market_open = True

    dashboard = build_dashboard(fresh_store)

    assert dashboard.market.status == "LIVE"


# --- Pipeline failure --------------------------------------------------------


def test_pipeline_failure_surfaces_as_unhealthy(fresh_store: EngineStore) -> None:
    # Simulate a poll that failed: the loop records last_error and the engine
    # keeps running. The dashboard must report unhealthy without raising.
    fresh_store.engine_running = True
    fresh_store.last_error = "RuntimeError: source unavailable"
    fresh_store.last_poll_at = None

    dashboard = build_dashboard(fresh_store)

    assert dashboard.engine.healthy is False
    assert dashboard.market.spot is None


def test_dashboard_after_recovery_is_healthy(fresh_store: EngineStore) -> None:
    _seed(fresh_store)
    fresh_store.last_error = None

    dashboard = build_dashboard(fresh_store)

    assert dashboard.engine.healthy is True


# --- Serialization -----------------------------------------------------------


def test_response_is_json_serializable_with_decimals(
    api: TestClient, fresh_store: EngineStore
) -> None:
    _seed(fresh_store)

    response = api.get("/api/v1/dashboard")

    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    # Decimals serialize as JSON numbers/strings, not Python objects.
    assert isinstance(body["option_chain"][0]["strike"], (int, float, str))


def test_data_age_is_deterministic_for_fixed_now() -> None:
    store = EngineStore()
    store.engine_running = True
    store.last_poll_at = dt.datetime(2026, 1, 1, 10, 0, tzinfo=dt.UTC)
    store.spot_price = Decimal("24700")
    now = dt.datetime(2026, 1, 1, 10, 0, 30, tzinfo=dt.UTC)

    first = build_dashboard(store, now=now)
    second = build_dashboard(store, now=now)

    assert first.engine.data_age_seconds == 30.0
    assert first.model_dump() == second.model_dump()
