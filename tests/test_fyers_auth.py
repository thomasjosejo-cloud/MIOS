"""Tests for the Fyers auth manager and OAuth endpoints."""

import datetime as dt
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mios.config import Settings
from mios.config.constants import AuthStatus
from mios.integrations.fyers.client import FyersAPIError, FyersAuthError
from mios.services.fyers_auth import (
    FyersAuthManager,
    FyersNotConfiguredError,
    get_auth_manager,
)
from mios.services.fyers_auth.session import FyersSession, SessionStore, build_session


def _settings(tmp_path: Path, *, oauth: bool = True) -> Settings:
    return Settings(
        FYERS_CLIENT_ID="APP-100" if oauth else None,
        FYERS_SECRET_KEY="secret" if oauth else None,
        FYERS_REDIRECT_URI="https://cb.example/callback" if oauth else None,
        FYERS_SESSION_PATH=str(tmp_path / "session.json"),
        FYERS_TOKEN_TTL_HOURS=12,
    )


# --- login URL ---------------------------------------------------------------


def test_login_url_contains_oauth_params(tmp_path: Path) -> None:
    manager = FyersAuthManager(_settings(tmp_path))

    url = manager.login_url()

    assert url.startswith("https://api-t1.fyers.in/api/v3/generate-authcode")
    assert "client_id=APP-100" in url
    assert "response_type=code" in url
    assert "redirect_uri=" in url


def test_login_url_requires_oauth_config(tmp_path: Path) -> None:
    manager = FyersAuthManager(_settings(tmp_path, oauth=False))

    with pytest.raises(FyersNotConfiguredError):
        manager.login_url()


# --- complete_login ----------------------------------------------------------


async def test_complete_login_persists_and_activates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    manager = FyersAuthManager(settings)
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(return_value="ACCESS-TOKEN"),
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=True)
    )

    session = await manager.complete_login("auth-code-123")

    assert session.access_token == "ACCESS-TOKEN"
    assert manager.is_authenticated
    assert manager.status() is AuthStatus.CONNECTED
    # Persisted for restart recovery.
    persisted = SessionStore(settings.FYERS_SESSION_PATH).load()
    assert persisted is not None
    assert persisted.access_token == "ACCESS-TOKEN"


async def test_complete_login_rejects_invalid_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = FyersAuthManager(_settings(tmp_path))
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(return_value="ACCESS-TOKEN"),
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=False)
    )

    with pytest.raises(FyersAuthError):
        await manager.complete_login("auth-code")

    assert not manager.is_authenticated


async def test_complete_login_propagates_exchange_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = FyersAuthManager(_settings(tmp_path))
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(side_effect=FyersAuthError("bad code")),
    )

    with pytest.raises(FyersAuthError):
        await manager.complete_login("bad")

    assert not manager.is_authenticated


# --- startup loading ---------------------------------------------------------


async def test_load_on_startup_restores_valid_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    SessionStore(settings.FYERS_SESSION_PATH).save(
        build_session(access_token="tok", client_id="APP-100", ttl_hours=12)
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=True)
    )
    manager = FyersAuthManager(settings)

    assert await manager.load_on_startup() is True
    assert manager.status() is AuthStatus.CONNECTED


async def test_load_on_startup_no_session(tmp_path: Path) -> None:
    manager = FyersAuthManager(_settings(tmp_path))

    assert await manager.load_on_startup() is False
    assert manager.status() is AuthStatus.NOT_AUTHENTICATED


async def test_load_on_startup_discards_expired(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    past = dt.datetime(2020, 1, 1, tzinfo=dt.UTC)
    SessionStore(settings.FYERS_SESSION_PATH).save(
        FyersSession(
            access_token="tok",
            client_id="APP-100",
            created_at=past,
            expires_at=past + dt.timedelta(hours=1),
        )
    )
    manager = FyersAuthManager(settings)

    assert await manager.load_on_startup() is False
    # Expired file is cleared.
    assert not Path(settings.FYERS_SESSION_PATH).exists()


async def test_load_on_startup_discards_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    SessionStore(settings.FYERS_SESSION_PATH).save(
        build_session(access_token="stale", client_id="APP-100", ttl_hours=12)
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=False)
    )
    manager = FyersAuthManager(settings)

    assert await manager.load_on_startup() is False
    assert not Path(settings.FYERS_SESSION_PATH).exists()


async def test_invalid_session_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An invalid stored session leaves us NOT_AUTHENTICATED; a fresh login recovers.
    settings = _settings(tmp_path)
    SessionStore(settings.FYERS_SESSION_PATH).save(
        build_session(access_token="stale", client_id="APP-100", ttl_hours=12)
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=False)
    )
    manager = FyersAuthManager(settings)
    assert await manager.load_on_startup() is False
    assert manager.status() is AuthStatus.NOT_AUTHENTICATED

    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(return_value="fresh-token"),
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=True)
    )
    await manager.complete_login("new-code")

    assert manager.status() is AuthStatus.CONNECTED


# --- endpoints ---------------------------------------------------------------


@pytest.fixture
def oauth_client(
    tmp_path: Path,
    healthy_infrastructure: None,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, FyersAuthManager, AsyncMock]]:
    """Test client with an OAuth-configured manager and a stubbed engine connect."""
    from mios.main import app

    manager = FyersAuthManager(_settings(tmp_path))
    connect = AsyncMock()
    monkeypatch.setattr(
        "mios.api.v1.endpoints.fyers.connect_authenticated_engine", connect
    )
    app.dependency_overrides[get_auth_manager] = lambda: manager
    try:
        with TestClient(app) as client:
            yield client, manager, connect
    finally:
        app.dependency_overrides.pop(get_auth_manager, None)


def test_login_returns_url_as_json(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
) -> None:
    client, _, _ = oauth_client

    response = client.get("/api/v1/fyers/login?json=1")

    assert response.status_code == status.HTTP_200_OK
    assert "generate-authcode" in response.json()["login_url"]


def test_login_redirects_by_default(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
) -> None:
    client, _, _ = oauth_client

    response = client.get("/api/v1/fyers/login", follow_redirects=False)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "generate-authcode" in response.headers["location"]


def test_login_unconfigured_returns_503(
    tmp_path: Path, healthy_infrastructure: None
) -> None:
    from mios.main import app

    manager = FyersAuthManager(_settings(tmp_path, oauth=False))
    app.dependency_overrides[get_auth_manager] = lambda: manager
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/fyers/login?json=1")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    finally:
        app.dependency_overrides.pop(get_auth_manager, None)


def test_callback_success_connects_engine(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, connect = oauth_client
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(return_value="ACCESS-TOKEN"),
    )
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.validate_token", AsyncMock(return_value=True)
    )

    response = client.get("/api/v1/fyers/callback?auth_code=code123&s=ok")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "connected"
    connect.assert_awaited_once()


def test_callback_missing_code_returns_400(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
) -> None:
    client, _, _ = oauth_client

    response = client.get("/api/v1/fyers/callback")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_callback_error_status_returns_400(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
) -> None:
    client, _, _ = oauth_client

    response = client.get("/api/v1/fyers/callback?s=error")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_callback_invalid_code_returns_401(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, connect = oauth_client
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(side_effect=FyersAuthError("invalid auth code")),
    )

    response = client.get("/api/v1/fyers/callback?auth_code=bad")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    connect.assert_not_awaited()


def test_callback_network_failure_returns_502(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, _ = oauth_client
    monkeypatch.setattr(
        "mios.services.fyers_auth.flow.exchange_auth_code",
        AsyncMock(side_effect=FyersAPIError("network down")),
    )

    response = client.get("/api/v1/fyers/callback?auth_code=code")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


def test_status_endpoint_reports_not_authenticated(
    oauth_client: tuple[TestClient, FyersAuthManager, AsyncMock],
) -> None:
    client, _, _ = oauth_client

    body = client.get("/api/v1/fyers/status").json()

    assert body["authentication"] == "NOT_AUTHENTICATED"
    assert body["client_id"] is None
