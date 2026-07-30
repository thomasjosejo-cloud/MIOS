"""Process-wide singletons for the live engine.

Mirrors the `database`/`cache`/`event_bus` singleton pattern from the
infrastructure layer: one shared `EngineStore` the API reads from, and one
`OptionsIntelEngine` managed by the application lifespan. The data source is
chosen from configuration — real Fyers when credentials are present, otherwise
the deterministic simulator.
"""

from mios.config import Settings
from mios.core.logging import get_logger
from mios.db.session import Database, database
from mios.integrations.fyers.client import FyersClient
from mios.integrations.fyers.market_data import MarketDataSource
from mios.integrations.fyers.simulator import SimulatedMarketDataSource
from mios.integrations.fyers.source import FyersMarketDataSource
from mios.services.options_intel.engine import OptionsIntelEngine
from mios.services.options_intel.store import EngineStore

logger = get_logger(__name__)

#: The single store the API endpoints read from.
store = EngineStore()

_engine: OptionsIntelEngine | None = None
_fyers_client: FyersClient | None = None


class OptionsEngineConfigError(RuntimeError):
    """The options engine is enabled but not correctly configured."""


def build_source(settings: Settings) -> MarketDataSource:
    """Return the configured market data source.

    Uses the live Fyers source when credentials are present; otherwise falls
    back to the deterministic simulator so the engine still runs in
    development and tests.
    """
    global _fyers_client

    if settings.fyers_configured:
        assert settings.FYERS_CLIENT_ID is not None
        assert settings.FYERS_ACCESS_TOKEN is not None
        _fyers_client = FyersClient(
            client_id=settings.FYERS_CLIENT_ID,
            access_token=settings.FYERS_ACCESS_TOKEN.get_secret_value(),
            timeout=settings.FYERS_REQUEST_TIMEOUT,
        )
        logger.info("Options engine using live Fyers data source")
        return FyersMarketDataSource(_fyers_client, settings)

    logger.warning(
        "Fyers credentials not configured; options engine using simulated data"
    )
    return SimulatedMarketDataSource(settings)


async def start_engine(settings: Settings, db: Database | None = None) -> None:
    """Build and start the live engine, if enabled by configuration."""
    global _engine

    if not settings.OPTIONS_ENGINE_ENABLED:
        logger.info("Options engine disabled (OPTIONS_ENGINE_ENABLED=false)")
        return
    if _engine is not None:
        return

    source = build_source(settings)
    _engine = OptionsIntelEngine(source, store, db or database, settings)
    _engine.start()


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
