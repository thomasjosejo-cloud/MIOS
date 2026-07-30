"""Fyers authentication and session management.

The single home for the Fyers OAuth lifecycle: login URL generation, auth-code
exchange, token validation, and durable session storage. A process-wide manager
singleton is provided via `get_auth_manager`.
"""

from functools import lru_cache

from mios.config import get_settings
from mios.services.fyers_auth.manager import (
    FyersAuthManager,
    FyersNotConfiguredError,
)
from mios.services.fyers_auth.session import FyersSession

__all__ = [
    "FyersAuthManager",
    "FyersNotConfiguredError",
    "FyersSession",
    "get_auth_manager",
    "reset_auth_manager",
]


@lru_cache
def get_auth_manager() -> FyersAuthManager:
    """Return the process-wide Fyers auth manager (FastAPI dependency)."""
    return FyersAuthManager(get_settings())


def reset_auth_manager() -> None:
    """Drop the cached manager so the next call rebuilds it (tests)."""
    get_auth_manager.cache_clear()
