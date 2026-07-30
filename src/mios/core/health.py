"""Infrastructure health probing.

Every check performs a real round-trip to the component it reports on; no status
is inferred from configuration alone.
"""

import time
from typing import Protocol

from mios.cache import cache
from mios.config.constants import ComponentStatus
from mios.db import database
from mios.events import event_bus
from mios.schemas.health import ComponentHealth


class Pingable(Protocol):
    """An infrastructure component whose connectivity can be verified."""

    async def ping(self) -> bool:
        """Return whether the component is reachable right now."""
        ...


#: Component name to its manager, in reporting order. `ping` is resolved at call
#: time so the managers stay patchable in tests.
COMPONENTS: dict[str, Pingable] = {
    "database": database,
    "redis": cache,
    "nats": event_bus,
}


async def probe(name: str, component: Pingable) -> ComponentHealth:
    """Run a single connectivity check, recording its latency."""
    started = time.perf_counter()
    reachable = await component.ping()
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    return ComponentHealth(
        name=name,
        status=ComponentStatus.UP if reachable else ComponentStatus.DOWN,
        latency_ms=latency_ms,
    )


async def check_all() -> dict[str, ComponentHealth]:
    """Probe every infrastructure component."""
    return {
        name: await probe(name, component) for name, component in COMPONENTS.items()
    }
