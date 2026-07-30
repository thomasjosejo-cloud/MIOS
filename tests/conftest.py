"""Shared test fixtures.

`.env.test` is loaded into the process environment before the application is
imported, so tests never depend on a developer's local `.env`. All
infrastructure is mocked — no PostgreSQL, Redis, or NATS instance is required.
"""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

ENV_TEST_FILE = Path(__file__).resolve().parents[1] / ".env.test"

# Must run before `mios.main` is imported, since the app is built at import time.
load_dotenv(ENV_TEST_FILE, override=True)

from mios.cache import cache  # noqa: E402
from mios.config import Settings, get_settings  # noqa: E402
from mios.db import database  # noqa: E402
from mios.events import event_bus  # noqa: E402


@pytest.fixture
def settings() -> Settings:
    """Return the cached application settings."""
    return get_settings()


@pytest.fixture
def healthy_infrastructure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch every infrastructure component to connect and report as reachable."""
    for component in (database, cache, event_bus):
        monkeypatch.setattr(component, "ping", AsyncMock(return_value=True))
        monkeypatch.setattr(component, "disconnect", AsyncMock(return_value=None))

    monkeypatch.setattr(database, "connect", lambda *args, **kwargs: None)
    monkeypatch.setattr(cache, "connect", lambda *args, **kwargs: None)
    monkeypatch.setattr(event_bus, "connect", AsyncMock(return_value=None))


@pytest.fixture
def client(healthy_infrastructure: None) -> Iterator[TestClient]:
    """Return a test client with the application lifespan active."""
    from mios.main import app

    with TestClient(app) as test_client:
        yield test_client
