"""Shared test fixtures.

`.env.test` is loaded into the process environment before the application is
imported, so tests never depend on a developer's local `.env`. All
infrastructure is mocked — no PostgreSQL, Redis, or NATS instance is required.
"""

import datetime as dt
from collections.abc import Callable, Iterator
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

ENV_TEST_FILE = Path(__file__).resolve().parents[1] / ".env.test"

# Must run before `mios.main` is imported, since the app is built at import time.
load_dotenv(ENV_TEST_FILE, override=True)

from mios.cache import cache  # noqa: E402
from mios.config import Settings, get_settings  # noqa: E402
from mios.db import database  # noqa: E402
from mios.events import event_bus  # noqa: E402
from mios.schemas.market import Candle, OptionQuote, OptionType  # noqa: E402

_T0 = dt.datetime(2026, 1, 1, 9, 15, tzinfo=dt.UTC)


@pytest.fixture
def make_option_quote() -> Callable[..., OptionQuote]:
    """Return a factory building an `OptionQuote` with sensible defaults."""

    def _make(
        *,
        strike: int,
        option_type: OptionType,
        premium: float = 100.0,
        oi: int = 10_000,
        volume: int = 1_000,
        minutes: int = 0,
    ) -> OptionQuote:
        return OptionQuote(
            symbol=f"NSE:NIFTY-{option_type.value}-{strike}",
            strike=Decimal(strike),
            option_type=option_type,
            expiry=dt.date(2026, 1, 8),
            premium=Decimal(str(premium)),
            oi=oi,
            volume=volume,
            timestamp=_T0 + dt.timedelta(minutes=minutes),
        )

    return _make


@pytest.fixture
def make_candles() -> Callable[[list[float]], list[Candle]]:
    """Return a factory building a candle series from a list of close prices.

    Wicks vary by index so adjacent candles never tie exactly on high/low,
    which would otherwise suppress fractal swing detection.
    """

    def _make(closes: list[float]) -> list[Candle]:
        candles: list[Candle] = []
        for i, close in enumerate(closes):
            open_ = closes[i - 1] if i > 0 else close
            wick = 0.15 + (i % 3) * 0.07
            high = max(open_, close) + wick
            low = min(open_, close) - wick
            candles.append(
                Candle(
                    symbol="NSE:NIFTY50-INDEX",
                    timestamp=_T0 + dt.timedelta(minutes=5 * i),
                    open=Decimal(str(round(open_, 2))),
                    high=Decimal(str(round(high, 2))),
                    low=Decimal(str(round(low, 2))),
                    close=Decimal(str(round(close, 2))),
                    volume=1_000 + i * 20,
                )
            )
        return candles

    return _make


@pytest.fixture
def zigzag_uptrend_closes() -> list[float]:
    """Close prices forming a clean HH-HL uptrend for structure tests."""
    closes: list[float] = []
    points = [24600, 24700, 24630, 24750, 24680, 24820]
    for i in range(len(points) - 1):
        start, end = points[i], points[i + 1]
        step = 1 if end > start else -1
        closes.extend(range(start, end, step))
    closes.append(points[-1])
    return [float(value) for value in closes]


@pytest.fixture
def settings() -> Settings:
    """Return the cached application settings."""
    return get_settings()


@pytest.fixture
def healthy_infrastructure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch every infrastructure component to connect and report as reachable."""
    for component in (database, cache, event_bus):
        monkeypatch.setattr(component, "ping", AsyncMock(return_value=True))
        monkeypatch.setattr(component, "disconnect", AsyncMock(return_value=None))

    monkeypatch.setattr(database, "connect", lambda *args, **kwargs: None)
    monkeypatch.setattr(cache, "connect", lambda *args, **kwargs: None)
    monkeypatch.setattr(event_bus, "connect", AsyncMock(return_value=None))


@pytest.fixture
def client(healthy_infrastructure: None) -> Iterator[TestClient]:
    """Return a test client with the application lifespan active."""
    from mios.main import app

    with TestClient(app) as test_client:
        yield test_client
