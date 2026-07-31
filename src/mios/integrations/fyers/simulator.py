"""Deterministic simulated market data.

Used for development and testing without Fyers credentials or during closed
market hours. Generates a plausible, reproducible NIFTY-like option chain and
candle series from a fixed seed — never random noise pretending to be live
data in production, since `OPTIONS_ENGINE_ENABLED` gates whether this or the
real Fyers source is used.
"""

import datetime as dt
import random
from decimal import Decimal

from mios.config import Settings
from mios.schemas.market import Candle, OptionQuote, OptionType, SpotQuote
from mios.services.options_intel.market_hours import is_market_open


class SimulatedMarketDataSource:
    """Deterministic stand-in for `FyersMarketDataSource`."""

    def __init__(self, settings: Settings, *, seed: int = 42) -> None:
        """Seed the deterministic generator."""
        self._settings = settings
        self._rng = random.Random(seed)
        self._spot = Decimal("24700")
        #: The prior trading day's close, held fixed across the session so the
        #: day's change is measured against a stable baseline (as with Fyers).
        self._prev_close = Decimal("24650")
        self._tick = 0

    async def get_spot(self) -> SpotQuote:
        """Return a slowly random-walking spot price."""
        self._tick += 1
        drift = Decimal(self._rng.uniform(-15, 15)).quantize(Decimal("0.05"))
        self._spot += drift
        return SpotQuote(
            symbol=self._settings.NIFTY_SPOT_SYMBOL,
            ltp=self._spot,
            prev_close=self._prev_close,
            timestamp=dt.datetime.now(dt.UTC),
        )

    async def get_option_chain(self) -> list[OptionQuote]:
        """Return a synthetic chain around the current simulated spot."""
        settings = self._settings
        step = settings.OPTION_STRIKE_STEP
        atm = round(self._spot / step) * step
        expiry = dt.datetime.now(dt.UTC).date() + dt.timedelta(
            days=self._days_to_expiry()
        )
        now = dt.datetime.now(dt.UTC)

        quotes: list[OptionQuote] = []
        for offset in range(
            -settings.OPTION_STRIKE_COUNT, settings.OPTION_STRIKE_COUNT + 1
        ):
            strike = Decimal(atm + offset * step)
            for option_type in (OptionType.CE, OptionType.PE):
                quotes.append(self._synthetic_quote(strike, option_type, expiry, now))

        return quotes

    def _synthetic_quote(
        self,
        strike: Decimal,
        option_type: OptionType,
        expiry: dt.date,
        now: dt.datetime,
    ) -> OptionQuote:
        """Build one strike's synthetic quote, biased by moneyness."""
        distance = abs(strike - self._spot)
        base_premium = max(Decimal(5), Decimal(300) - distance / 4)
        base_oi = max(1000, 50000 - int(distance) * 20)

        return OptionQuote(
            symbol=f"NSE:NIFTY-{option_type.value}-{strike}",
            strike=strike,
            option_type=option_type,
            expiry=expiry,
            premium=(base_premium + Decimal(self._rng.uniform(-5, 5))).quantize(
                Decimal("0.05")
            ),
            oi=max(0, base_oi + self._rng.randint(-2000, 2000)),
            volume=max(0, self._rng.randint(0, 20000)),
            timestamp=now,
        )

    async def get_candles(self) -> list[Candle]:
        """Return a synthetic 5-minute candle series ending at the current spot."""
        settings = self._settings
        count = settings.CANDLE_LOOKBACK_COUNT
        now = dt.datetime.now(dt.UTC)
        price = self._spot - Decimal(count)

        candles: list[Candle] = []
        for i in range(count):
            timestamp = now - dt.timedelta(
                minutes=(count - i) * settings.CANDLE_RESOLUTION_MINUTES
            )
            open_ = price
            close = price + Decimal(self._rng.uniform(-8, 10)).quantize(Decimal("0.05"))
            high = max(open_, close) + Decimal(self._rng.uniform(0, 4))
            low = min(open_, close) - Decimal(self._rng.uniform(0, 4))
            candles.append(
                Candle(
                    symbol=settings.NIFTY_SPOT_SYMBOL,
                    timestamp=timestamp,
                    open=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=self._rng.randint(1000, 5000),
                )
            )
            price = close

        return candles

    async def get_market_open(self) -> bool:
        """Return whether the market is open, per the configured trading hours."""
        return is_market_open(self._settings)

    @staticmethod
    def _days_to_expiry() -> int:
        """Return days until the next Thursday, NIFTY's weekly expiry day."""
        today = dt.datetime.now(dt.UTC).date()
        return (3 - today.weekday()) % 7 or 7
