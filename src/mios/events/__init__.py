"""Event Bus infrastructure (NATS JetStream)."""

from mios.events.client import EventBus, event_bus, get_jetstream

__all__ = ["EventBus", "event_bus", "get_jetstream"]
