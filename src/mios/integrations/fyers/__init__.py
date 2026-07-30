"""Fyers API v3 integration.

The only component permitted to talk to Fyers. Callers receive normalized
Pydantic schemas (`mios.schemas.market`) or raw JSON for the one-time auth
exchange — never a Fyers-specific object.
"""

from mios.integrations.fyers.client import FyersAPIError, FyersAuthError, FyersClient
from mios.integrations.fyers.market_data import MarketDataSource
from mios.integrations.fyers.simulator import SimulatedMarketDataSource
from mios.integrations.fyers.source import FyersMarketDataSource

__all__ = [
    "FyersAPIError",
    "FyersAuthError",
    "FyersClient",
    "FyersMarketDataSource",
    "MarketDataSource",
    "SimulatedMarketDataSource",
]
