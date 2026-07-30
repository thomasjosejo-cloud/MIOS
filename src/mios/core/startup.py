"""Infrastructure startup and shutdown sequencing.

Connections are established in dependency order and torn down in reverse. When
`STARTUP_VALIDATION` is enabled, an unreachable mandatory component aborts
startup rather than letting the application serve traffic it cannot fulfil.
"""

from mios.cache import cache
from mios.config import Settings
from mios.config.constants import ComponentStatus
from mios.core.health import check_all
from mios.core.logging import get_logger
from mios.db import database
from mios.db.timescale import verify_timescaledb
from mios.events import event_bus

logger = get_logger(__name__)


class StartupError(RuntimeError):
    """Raised when a mandatory infrastructure component is unavailable."""


async def connect_infrastructure(settings: Settings) -> None:
    """Connect every infrastructure component and validate connectivity."""
    database.connect(settings)
    cache.connect(settings)

    # A failed NATS connection is reported uniformly by _validate below, so the
    # fail-fast decision lives in one place.
    try:
        await event_bus.connect(settings)
    except Exception as error:
        logger.error("NATS connection failed", extra={"error": str(error)})

    await _validate(settings)


async def _validate(settings: Settings) -> None:
    """Probe all components, failing fast when validation is enabled."""
    components = await check_all()

    for name, component in components.items():
        if component.status is ComponentStatus.UP:
            logger.info(
                "%s connected",
                name,
                extra={"component": name, "latency_ms": component.latency_ms},
            )
        else:
            logger.error("%s unavailable", name, extra={"component": name})

    unavailable = [
        name
        for name, component in components.items()
        if component.status is ComponentStatus.DOWN
    ]

    if unavailable and settings.STARTUP_VALIDATION:
        msg = f"Mandatory infrastructure unavailable: {', '.join(unavailable)}"
        raise StartupError(msg)

    if settings.TIMESCALEDB_ENABLED and "database" not in unavailable:
        try:
            await verify_timescaledb(database.engine)
        except Exception as error:
            logger.error("TimescaleDB validation failed", extra={"error": str(error)})
            if settings.STARTUP_VALIDATION:
                raise StartupError(str(error)) from error


async def disconnect_infrastructure() -> None:
    """Disconnect every component in reverse order, tolerating failures."""
    for name, disconnect in (
        ("NATS", event_bus.disconnect),
        ("Redis", cache.disconnect),
        ("Database", database.disconnect),
    ):
        try:
            await disconnect()
        except Exception:
            logger.exception("%s shutdown failed", name)
