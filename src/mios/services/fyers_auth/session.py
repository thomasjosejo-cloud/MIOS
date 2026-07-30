"""Fyers session model and persistence.

A session is the durable record of a completed OAuth login: the access token
plus the metadata needed to reason about it. It is stored as JSON at the
configured path (default `data/fyers/session.json`) so a login survives
restarts. The token is a secret and is never logged.
"""

import datetime as dt
import json
from pathlib import Path

from pydantic import BaseModel

from mios.core.logging import get_logger

logger = get_logger(__name__)


class FyersSession(BaseModel):
    """A persisted Fyers OAuth session."""

    access_token: str
    client_id: str
    created_at: dt.datetime
    expires_at: dt.datetime

    def is_expired(self, *, now: dt.datetime | None = None) -> bool:
        """Whether the token is past its soft expiry (a fast pre-check)."""
        return (now or dt.datetime.now(dt.UTC)) >= self.expires_at

    def masked(self) -> dict[str, object]:
        """Return a log-safe view that never exposes the token."""
        return {
            "client_id": self.client_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "token": "***",
        }


class SessionStore:
    """Reads and writes the session JSON file."""

    def __init__(self, path: str | Path) -> None:
        """Bind the store to the session file path."""
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """The session file path."""
        return self._path

    def load(self) -> FyersSession | None:
        """Load the persisted session, or `None` if absent or unreadable."""
        if not self._path.exists():
            return None
        try:
            data = json.loads(self._path.read_text())
            return FyersSession.model_validate(data)
        except (OSError, ValueError) as error:
            logger.warning("Ignoring unreadable Fyers session file: %s", error)
            return None

    def save(self, session: FyersSession) -> None:
        """Persist the session, creating parent directories and restricting mode."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(session.model_dump_json(indent=2))
        # Token file: readable/writable by the owner only.
        try:
            self._path.chmod(0o600)
        except OSError:  # pragma: no cover - filesystem may not support chmod
            pass
        logger.info("Fyers session saved", extra=session.masked())

    def clear(self) -> None:
        """Remove the session file if present."""
        self._path.unlink(missing_ok=True)


def build_session(
    *,
    access_token: str,
    client_id: str,
    ttl_hours: float,
    now: dt.datetime | None = None,
) -> FyersSession:
    """Construct a session with a soft expiry `ttl_hours` after `now`."""
    created = now or dt.datetime.now(dt.UTC)
    return FyersSession(
        access_token=access_token,
        client_id=client_id,
        created_at=created,
        expires_at=created + dt.timedelta(hours=ttl_hours),
    )
