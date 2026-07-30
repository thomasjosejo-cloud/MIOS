"""Tests for the health endpoint."""

from fastapi.testclient import TestClient

from mios.config import get_settings


def test_health_returns_healthy(client: TestClient) -> None:
    settings = get_settings()

    response = client.get(f"{settings.API_PREFIX}/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


def test_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200
