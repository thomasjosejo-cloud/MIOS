"""Fyers-backed implementation of `MarketDataSource`.

Wires the raw `FyersClient` transport through the normalizer, so the engine
orchestrator only ever sees normalized schemas.
"""

import datetime as dt

from mios.config import Settings
from mios.integrations.fyers.client import FyersClient
from mios.integrations.fyers.normalizer import (
    normalize_candles,
    normalize_option_chain,
    normalize_spot,
)
from mios.schemas.market import Candle, OptionQuote, SpotQuote
from mios.services.options_intel.market_hours import is_market_open


class FyersMarketDataSource:
    """Live market data sourced from Fyers, normalized before leaving this class."""

    def __init__(self, client: FyersClient, settings: Settings) -> None:
        """Wrap a Fyers client with the active settings."""
        self._client = client
        self._settings = settings

    async def get_spot(self) -> SpotQuote:
        """Return the latest NIFTY spot quote."""
        symbol = self._settings.NIFTY_SPOT_SYMBOL
        raw = await self._client.quotes([symbol])
        return normalize_spot(raw, symbol)

    async def get_option_chain(self) -> list[OptionQuote]:
        """Return the latest observation for every tracked NIFTY strike."""
        raw = await self._client.option_chain(
            self._settings.NIFTY_SPOT_SYMBOL,
            strike_count=self._settings.OPTION_STRIKE_COUNT,
            timestamp=self._settings.OPTION_EXPIRY_TIMESTAMP,
        )
        return normalize_option_chain(raw, symbol=self._settings.NIFTY_SPOT_SYMBOL)

    async def get_candles(self) -> list[Candle]:
        """Return recent 5-minute NIFTY candles, oldest first."""
        settings = self._settings
        now = dt.datetime.now(dt.UTC)
        lookback_minutes = (
            settings.CANDLE_LOOKBACK_COUNT * settings.CANDLE_RESOLUTION_MINUTES
        )
        range_from = now - dt.timedelta(minutes=lookback_minutes)

        raw = await self._client.history(
            settings.NIFTY_SPOT_SYMBOL,
            # Fyers accepts plain minute counts as strings for intraday resolutions.
            resolution=str(settings.CANDLE_RESOLUTION_MINUTES),
            range_from=int(range_from.timestamp()),
            range_to=int(now.timestamp()),
        )
        return normalize_candles(raw, symbol=settings.NIFTY_SPOT_SYMBOL)

    async def get_market_open(self) -> bool:
        """Return whether the market is open, per the configured trading hours."""
        return is_market_open(self._settings)
