"""Fyers authentication session manager.

The one component that owns the Fyers session lifecycle end-to-end: generate the
login URL, exchange an auth code, validate a token, persist and load the
session, report status, and hand out an authenticated `FyersClient`. Nothing
else in MIOS performs Fyers authentication.
"""

import secrets

from mios.config import Settings
from mios.config.constants import AuthStatus
from mios.core.logging import get_logger
from mios.integrations.fyers.client import FyersAuthError, FyersClient
from mios.services.fyers_auth import flow
from mios.services.fyers_auth.session import (
    FyersSession,
    SessionStore,
    build_session,
)

logger = get_logger(__name__)


class FyersNotConfiguredError(RuntimeError):
    """OAuth is not configured (missing client id, secret, or redirect URI)."""


class FyersAuthManager:
    """Owns the Fyers OAuth session for the process."""

    def __init__(self, settings: Settings) -> None:
        """Bind the manager to settings and the configured session file."""
        self._settings = settings
        self._store = SessionStore(settings.FYERS_SESSION_PATH)
        self._session: FyersSession | None = None

    # --- status -------------------------------------------------------------

    @property
    def session(self) -> FyersSession | None:
        """The current in-memory session, if authenticated."""
        return self._session

    @property
    def is_authenticated(self) -> bool:
        """Whether a validated session is currently held."""
        return self._session is not None

    def status(self) -> AuthStatus:
        """Report the coarse authentication status for the dashboard."""
        return (
            AuthStatus.CONNECTED
            if self.is_authenticated
            else AuthStatus.NOT_AUTHENTICATED
        )

    # --- login flow ---------------------------------------------------------

    def login_url(self) -> str:
        """Build the Fyers hosted-login URL, requiring OAuth configuration."""
        self._require_oauth_config()
        assert self._settings.FYERS_CLIENT_ID is not None  # narrowed by the guard
        assert self._settings.FYERS_REDIRECT_URI is not None
        return flow.login_url(
            client_id=self._settings.FYERS_CLIENT_ID,
            redirect_uri=self._settings.FYERS_REDIRECT_URI,
            state=secrets.token_urlsafe(16),
        )

    async def complete_login(self, auth_code: str) -> FyersSession:
        """Exchange an auth code, validate it, persist and activate the session."""
        self._require_oauth_config()
        settings = self._settings
        assert settings.FYERS_CLIENT_ID is not None
        assert settings.FYERS_SECRET_KEY is not None

        access_token = await flow.exchange_auth_code(
            client_id=settings.FYERS_CLIENT_ID,
            secret_key=settings.FYERS_SECRET_KEY.get_secret_value(),
            auth_code=auth_code,
            timeout=settings.FYERS_REQUEST_TIMEOUT,
        )

        valid = await flow.validate_token(
            client_id=settings.FYERS_CLIENT_ID,
            access_token=access_token,
            probe_symbol=settings.NIFTY_SPOT_SYMBOL,
            timeout=settings.FYERS_REQUEST_TIMEOUT,
        )
        if not valid:
            raise FyersAuthError("Exchanged token failed live validation")

        session = build_session(
            access_token=access_token,
            client_id=settings.FYERS_CLIENT_ID,
            ttl_hours=settings.FYERS_TOKEN_TTL_HOURS,
        )
        self._store.save(session)
        self._session = session
        logger.info("Fyers login completed", extra=session.masked())
        return session

    # --- startup ------------------------------------------------------------

    async def load_on_startup(self) -> bool:
        """Load and validate a persisted session on startup.

        Returns whether the engine can connect. Never raises: a missing,
        expired, or invalid session simply yields `False`, leaving the engine
        to wait for a browser login.
        """
        session = self._store.load()
        if session is None:
            logger.info("No Fyers session found; awaiting login")
            return False

        if session.is_expired():
            logger.info("Stored Fyers session expired; awaiting re-login")
            self._store.clear()
            return False

        valid = await flow.validate_token(
            client_id=session.client_id,
            access_token=session.access_token,
            probe_symbol=self._settings.NIFTY_SPOT_SYMBOL,
            timeout=self._settings.FYERS_REQUEST_TIMEOUT,
        )
        if not valid:
            logger.info("Stored Fyers session no longer valid; awaiting re-login")
            self._store.clear()
            return False

        self._session = session
        logger.info("Fyers session restored", extra=session.masked())
        return True

    # --- client -------------------------------------------------------------

    def build_client(self) -> FyersClient:
        """Return an authenticated client, requiring an active session."""
        if self._session is None:
            raise FyersAuthError("No active Fyers session")
        return FyersClient(
            client_id=self._session.client_id,
            access_token=self._session.access_token,
            timeout=self._settings.FYERS_REQUEST_TIMEOUT,
        )

    def logout(self) -> None:
        """Clear the active session and remove the persisted file."""
        self._session = None
        self._store.clear()

    # --- internals ----------------------------------------------------------

    def _require_oauth_config(self) -> None:
        if not self._settings.fyers_oauth_configured:
            raise FyersNotConfiguredError(
                "Fyers OAuth is not configured; set FYERS_CLIENT_ID, "
                "FYERS_SECRET_KEY and FYERS_REDIRECT_URI"
            )
