"""Tests for the /market/* API endpoints."""

from collections.abc import Iterator

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mios.config import Settings
from mios.integrations.fyers import SimulatedMarketDataSource
from mios.services.options_intel import runtime
from mios.services.options_intel.engine import OptionsIntelEngine
from mios.services.options_intel.store import EngineStore


@pytest.fixture
def api(
    healthy_infrastructure: None, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """Return a test client with a fresh, monkeypatched engine store."""
    fresh = EngineStore()
    monkeypatch.setattr(runtime, "store", fresh)
    from mios.main import app

    with TestClient(app) as client:
        yield client


async def _seed(store: EngineStore) -> None:
    from unittest.mock import MagicMock

    settings = Settings(OPTION_STRIKE_COUNT=5, CANDLE_LOOKBACK_COUNT=30)
    db = MagicMock()
    db.is_connected = False
    engine = OptionsIntelEngine(
        SimulatedMarketDataSource(settings), store, db, settings
    )
    await engine.poll_once()
    await engine.poll_once()


def _seed_sync(store: EngineStore) -> None:
    """Drive two async polls to populate the store from a synchronous test."""
    import asyncio

    asyncio.run(_seed(store))


def test_status_is_available_before_any_poll(api: TestClient) -> None:
    response = api.get("/api/v1/market/status")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["engine_running"] is False
    assert "session" in body


def test_analysis_endpoints_503_before_any_poll(api: TestClient) -> None:
    for path in ("context", "options", "recommendation", "radar", "structure"):
        response = api.get(f"/api/v1/market/{path}")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_endpoints_serve_seeded_data(api: TestClient) -> None:
    _seed_sync(runtime.store)

    context = api.get("/api/v1/market/context")
    assert context.status_code == status.HTTP_200_OK
    assert "controlling_side" in context.json()

    options = api.get("/api/v1/market/options")
    assert options.status_code == status.HTTP_200_OK
    assert options.json()["strikes"]

    recommendation = api.get("/api/v1/market/recommendation")
    assert recommendation.status_code == status.HTTP_200_OK
    body = recommendation.json()
    assert "decision" in body
    assert "confidence" in body
    assert "gates" in body

    radar = api.get("/api/v1/market/radar")
    assert radar.status_code == status.HTTP_200_OK
    assert "highest_volume" in radar.json()

    structure = api.get("/api/v1/market/structure")
    assert structure.status_code == status.HTTP_200_OK
    assert "structure" in structure.json()
    assert "momentum" in structure.json()
