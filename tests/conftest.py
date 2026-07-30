"""Shared test fixtures.

`.env.test` is loaded into the process environment before the application is
imported, so tests never depend on a developer's local `.env`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

ENV_TEST_FILE = Path(__file__).resolve().parents[1] / ".env.test"

load_dotenv(ENV_TEST_FILE, override=True)


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a test client with the application lifespan active."""
    from mios.main import app

    with TestClient(app) as test_client:
        yield test_client
