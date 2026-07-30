"""Tests for Fyers session persistence."""

import datetime as dt
from pathlib import Path

from mios.services.fyers_auth.session import (
    FyersSession,
    SessionStore,
    build_session,
)


def test_build_session_sets_soft_expiry() -> None:
    now = dt.datetime(2026, 1, 1, 9, 0, tzinfo=dt.UTC)
    session = build_session(
        access_token="tok", client_id="APP-100", ttl_hours=12, now=now
    )

    assert session.access_token == "tok"
    assert session.client_id == "APP-100"
    assert session.created_at == now
    assert session.expires_at == now + dt.timedelta(hours=12)
    assert session.is_expired(now=now) is False
    assert session.is_expired(now=now + dt.timedelta(hours=13)) is True


def test_masked_never_exposes_token() -> None:
    session = build_session(access_token="secret-token", client_id="APP", ttl_hours=1)

    masked = session.masked()

    assert masked["token"] == "***"
    assert "secret-token" not in str(masked)


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "fyers" / "session.json"
    store = SessionStore(path)
    session = build_session(access_token="tok", client_id="APP-100", ttl_hours=12)

    store.save(session)

    assert path.exists()
    loaded = store.load()
    assert loaded is not None
    assert loaded.access_token == "tok"
    assert loaded.client_id == "APP-100"


def test_load_missing_file_returns_none(tmp_path: Path) -> None:
    assert SessionStore(tmp_path / "nope.json").load() is None


def test_load_corrupt_file_returns_none(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    path.write_text("{ not valid json")

    assert SessionStore(path).load() is None


def test_clear_removes_file(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    store = SessionStore(path)
    store.save(build_session(access_token="t", client_id="A", ttl_hours=1))
    assert path.exists()

    store.clear()

    assert not path.exists()
    store.clear()  # idempotent


def test_saved_file_is_owner_only(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    SessionStore(path).save(build_session(access_token="t", client_id="A", ttl_hours=1))

    assert (path.stat().st_mode & 0o777) == 0o600


def test_session_model_validates_types() -> None:
    session = FyersSession.model_validate(
        {
            "access_token": "t",
            "client_id": "A",
            "created_at": "2026-01-01T09:00:00+00:00",
            "expires_at": "2026-01-01T21:00:00+00:00",
        }
    )

    assert session.client_id == "A"
