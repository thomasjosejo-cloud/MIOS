"""Tests for the health endpoint."""

from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mios.cache import cache
from mios.config import Settings
from mios.db import database
from mios.events import event_bus


def test_health_reports_all_components_up(
    client: TestClient, settings: Settings
) -> None:
    response = client.get(f"{settings.API_PREFIX}/health")
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["status"] == "healthy"
    assert body["application"] == settings.APP_NAME
    assert body["version"] == settings.APP_VERSION
    assert body["environment"] == "testing"
    assert set(body["components"]) == {"database", "redis", "nats"}
    assert all(component["status"] == "up" for component in body["components"].values())


def test_health_reports_latency_per_component(
    client: TestClient, settings: Settings
) -> None:
    body = client.get(f"{settings.API_PREFIX}/health").json()

    for component in body["components"].values():
        assert isinstance(component["latency_ms"], float)
        assert component["latency_ms"] >= 0


@pytest.mark.parametrize("failing", ["database", "redis", "nats"])
def test_health_is_degraded_when_a_component_is_down(
    client: TestClient,
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    failing: str,
) -> None:
    components = {"database": database, "redis": cache, "nats": event_bus}
    monkeypatch.setattr(components[failing], "ping", AsyncMock(return_value=False))

    response = client.get(f"{settings.API_PREFIX}/health")
    body = response.json()

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert body["status"] == "degraded"
    assert body["components"][failing]["status"] == "down"

    for name, component in body["components"].items():
        if name != failing:
            assert component["status"] == "up"


def test_health_verifies_connectivity_on_every_request(
    client: TestClient, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Status must come from a live probe, not a cached or static value."""
    ping = AsyncMock(return_value=True)
    monkeypatch.setattr(database, "ping", ping)

    client.get(f"{settings.API_PREFIX}/health")
    client.get(f"{settings.API_PREFIX}/health")

    assert ping.await_count == 2


def test_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == status.HTTP_200_OK
    assert client.get("/openapi.json").status_code == status.HTTP_200_OK
