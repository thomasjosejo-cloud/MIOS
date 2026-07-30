"""The market data source contract the live engine polls against.

Implemented by `FyersMarketDataSource` (real data) and
`SimulatedMarketDataSource` (deterministic data for tests and credential-free
development), so the engine orchestrator never depends on Fyers directly.
"""

from typing import Protocol

from mios.schemas.market import Candle, OptionQuote, SpotQuote


class MarketDataSource(Protocol):
    """A source of normalized spot, option chain, and candle data."""

    async def get_spot(self) -> SpotQuote:
        """Return the latest spot quote."""
        ...

    async def get_option_chain(self) -> list[OptionQuote]:
        """Return the latest observation for every tracked strike."""
        ...

    async def get_candles(self) -> list[Candle]:
        """Return recent OHLCV candles, oldest first."""
        ...

    async def get_market_open(self) -> bool:
        """Return whether the underlying market is currently open."""
        ...
