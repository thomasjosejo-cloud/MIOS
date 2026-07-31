"""Process-wide singletons for the live engine.

Mirrors the `database`/`cache`/`event_bus` singleton pattern: one shared
`EngineStore` the API reads from, and one `OptionsIntelEngine` managed by the
application lifespan.

Data-source selection is authentication-driven (Sprint 8). When a valid Fyers
session exists the engine connects to live Fyers data; otherwise it waits for a
browser login (`/api/v1/fyers/login`) and connects automatically once the
callback completes. The deterministic simulator is used only when
`FYERS_USE_SIMULATOR` is set, for development and tests.
"""

from mios.config import Settings
from mios.config.constants import ConnectionState, DataSource
from mios.core.logging import get_logger
from mios.db.session import Database, database
from mios.integrations.fyers.client import FyersClient
from mios.integrations.fyers.market_data import MarketDataSource
from mios.integrations.fyers.simulator import SimulatedMarketDataSource
from mios.integrations.fyers.source import FyersMarketDataSource
from mios.services.fyers_auth import get_auth_manager
from mios.services.options_intel.engine import OptionsIntelEngine
from mios.services.options_intel.store import EngineStore

logger = get_logger(__name__)

#: The single store the API endpoints read from.
store = EngineStore()

_engine: OptionsIntelEngine | None = None
_fyers_client: FyersClient | None = None


def set_connection_state(state: ConnectionState) -> None:
    """Update the connection state reported on the dashboard."""
    store.connection_state = state


async def _resolve_source(settings: Settings) -> MarketDataSource | None:
    """Choose the market data source, or `None` when authentication is pending."""
    global _fyers_client

    manager = get_auth_manager()
    if manager.is_authenticated:
        _fyers_client = manager.build_client()
        store.authenticated = True
        store.data_source = DataSource.FYERS
        store.connection_state = ConnectionState.CONNECTED
        logger.info("Options engine using live Fyers data source")
        return FyersMarketDataSource(_fyers_client, settings)

    if settings.FYERS_USE_SIMULATOR:
        store.authenticated = False
        store.data_source = DataSource.SIMULATOR
        # The simulator is not a Fyers connection; report it honestly.
        store.connection_state = ConnectionState.NOT_CONNECTED
        logger.warning("FYERS_USE_SIMULATOR set; engine using simulated data")
        return SimulatedMarketDataSource(settings)

    store.authenticated = False
    store.data_source = DataSource.NONE
    return None


async def start_engine(settings: Settings, db: Database | None = None) -> None:
    """Start the engine if enabled, loading any persisted Fyers session first.

    When enabled but not authenticated (and simulator is off), the engine waits:
    it is not started here, but connects later via `connect_authenticated_engine`
    once a login completes.
    """
    global _engine

    if not settings.OPTIONS_ENGINE_ENABLED:
        logger.info("Options engine disabled (OPTIONS_ENGINE_ENABLED=false)")
        return
    if _engine is not None:
        return

    # Restore a persisted session so a restart reconnects without a new login.
    if settings.fyers_oauth_configured:
        await get_auth_manager().load_on_startup()

    source = await _resolve_source(settings)
    if source is None:
        # Preserve an explicit SESSION_EXPIRED/AUTHENTICATION_FAILED set by the
        # caller; only default to NOT_CONNECTED from a neutral state.
        if store.connection_state is ConnectionState.CONNECTED:
            store.connection_state = ConnectionState.NOT_CONNECTED
        logger.info(
            "Options engine enabled; awaiting Fyers login at /api/v1/fyers/login"
        )
        return

    _engine = OptionsIntelEngine(
        source, store, db or database, settings, on_session_expired=_handle_expiry
    )
    _engine.start()


async def connect_authenticated_engine(
    settings: Settings, db: Database | None = None
) -> None:
    """(Re)start the engine after a successful login, replacing any prior source."""
    await stop_engine()
    await start_engine(settings, db)


async def _handle_expiry() -> None:
    """Handle a mid-session token expiry: clear the session, return to prompt.

    Invoked by the engine loop after a poll fails authentication. The engine
    has already stopped its own loop, so this only tears down shared state so a
    fresh login can reconnect.
    """
    global _engine, _fyers_client

    get_auth_manager().logout()
    store.authenticated = False
    store.data_source = DataSource.NONE
    store.connection_state = ConnectionState.SESSION_EXPIRED
    _engine = None
    if _fyers_client is not None:
        await _fyers_client.aclose()
        _fyers_client = None
    logger.warning("Fyers session cleared; awaiting re-login")


async def stop_engine() -> None:
    """Stop the live engine and release the Fyers client, if running."""
    global _engine, _fyers_client

    if _engine is not None:
        await _engine.stop()
        _engine = None
    if _fyers_client is not None:
        await _fyers_client.aclose()
        _fyers_client = None


def get_store() -> EngineStore:
    """Return the shared engine store (FastAPI dependency)."""
    return store
