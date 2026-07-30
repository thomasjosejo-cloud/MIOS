"""NATS JetStream connection lifecycle.

Implements the Event Bus transport connection defined in `docs/06-event-bus.md`.
Provides the connection and JetStream context only — no streams, publishers, or
subscribers are declared here.
"""

import asyncio

import nats
from nats.aio.client import Client as NATSClient
from nats.js import JetStreamContext

from mios.config import Settings, get_settings
from mios.core.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """Owns the NATS connection and its JetStream context."""

    def __init__(self) -> None:
        """Create an unconnected event bus handle."""
        self._client: NATSClient | None = None
        self._jetstream: JetStreamContext | None = None

    @property
    def client(self) -> NATSClient:
        """Return the active connection, or fail if NATS is not connected."""
        if self._client is None:
            msg = "NATS is not connected; call connect() during startup"
            raise RuntimeError(msg)
        return self._client

    @property
    def jetstream(self) -> JetStreamContext:
        """Return the JetStream context, or fail if NATS is not connected."""
        if self._jetstream is None:
            msg = "NATS is not connected; call connect() during startup"
            raise RuntimeError(msg)
        return self._jetstream

    @property
    def is_connected(self) -> bool:
        """Whether the underlying connection is currently established."""
        return self._client is not None and self._client.is_connected

    async def connect(self, settings: Settings | None = None) -> None:
        """Open the connection and acquire the JetStream context.

        The initial connection is bounded by an explicit deadline. With
        `max_reconnect_attempts=-1` the client retries the first connection
        forever, which would hang startup instead of failing fast; the deadline
        keeps the reconnect policy unlimited while startup stays bounded.
        """
        if self._client is not None:
            return

        settings = settings or get_settings()
        budget = settings.NATS_CONNECT_TIMEOUT * max(len(settings.NATS_SERVERS), 1)

        async with asyncio.timeout(budget):
            self._client = await nats.connect(
                servers=settings.NATS_SERVERS,
                connect_timeout=settings.NATS_CONNECT_TIMEOUT,
                max_reconnect_attempts=settings.NATS_MAX_RECONNECT_ATTEMPTS,
                reconnect_time_wait=settings.NATS_RECONNECT_TIME_WAIT,
                ping_interval=settings.NATS_PING_INTERVAL,
                error_cb=self._on_error,
                disconnected_cb=self._on_disconnected,
                reconnected_cb=self._on_reconnected,
                closed_cb=self._on_closed,
            )

        self._jetstream = self._client.jetstream()
        logger.info("NATS connected", extra={"servers": settings.NATS_SERVERS})

    async def disconnect(self) -> None:
        """Drain in-flight messages, then close the connection."""
        if self._client is None:
            return

        try:
            await self._client.drain()
        except Exception:
            logger.exception("NATS drain failed; closing connection")
            await self._client.close()

        self._client = None
        self._jetstream = None
        logger.info("NATS disconnected")

    async def ping(self) -> bool:
        """Verify real connectivity with a server round-trip."""
        if self._client is None or not self._client.is_connected:
            return False

        try:
            await self._client.flush(timeout=2)
        except Exception:
            logger.exception("NATS ping failed")
            return False
        return True

    @staticmethod
    async def _on_error(error: Exception) -> None:
        """Log asynchronous connection errors reported by the client."""
        logger.error("NATS error", extra={"error": str(error)})

    @staticmethod
    async def _on_disconnected() -> None:
        """Log an unexpected disconnection."""
        logger.warning("NATS disconnected; reconnect attempts starting")

    @staticmethod
    async def _on_reconnected() -> None:
        """Log a successful reconnection."""
        logger.info("NATS reconnected")

    @staticmethod
    async def _on_closed() -> None:
        """Log permanent closure of the connection."""
        logger.info("NATS connection closed")


event_bus = EventBus()


def get_jetstream() -> JetStreamContext:
    """FastAPI dependency returning the shared JetStream context."""
    return event_bus.jetstream
