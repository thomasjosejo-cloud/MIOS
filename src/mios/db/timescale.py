"""TimescaleDB startup validation.

Confirms the extension is present so future Market Store migrations can create
hypertables. No hypertables are created here.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from mios.config.constants import TIMESCALEDB_EXTENSION
from mios.core.logging import get_logger

logger = get_logger(__name__)

_INSTALLED_VERSION = text("SELECT extversion FROM pg_extension WHERE extname = :name")
_IS_AVAILABLE = text(
    "SELECT default_version FROM pg_available_extensions WHERE name = :name"
)


async def verify_timescaledb(engine: AsyncEngine) -> str | None:
    """Return the installed TimescaleDB version, or `None` if not installed.

    Logs a warning when the extension is available but not yet enabled, and
    raises when the server cannot provide it at all.
    """
    params = {"name": TIMESCALEDB_EXTENSION}

    async with engine.connect() as connection:
        installed = (await connection.execute(_INSTALLED_VERSION, params)).scalar()
        if installed is not None:
            logger.info("TimescaleDB extension active", extra={"version": installed})
            return str(installed)

        available = (await connection.execute(_IS_AVAILABLE, params)).scalar()

    if available is None:
        msg = (
            "TimescaleDB extension is not available on this PostgreSQL server; "
            "use a TimescaleDB-enabled image or set TIMESCALEDB_ENABLED=false"
        )
        raise RuntimeError(msg)

    logger.warning(
        "TimescaleDB extension available but not enabled; a migration must run "
        "CREATE EXTENSION before hypertables can be created",
        extra={"available_version": available},
    )
    return None
