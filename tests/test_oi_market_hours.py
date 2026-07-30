"""Tests for the configured market-hours check."""

import datetime as dt
from zoneinfo import ZoneInfo

from mios.config import Settings
from mios.services.options_intel.market_hours import is_market_open

_IST = ZoneInfo("Asia/Kolkata")


def _at(year: int, month: int, day: int, hour: int, minute: int) -> dt.datetime:
    return dt.datetime(year, month, day, hour, minute, tzinfo=_IST)


def test_open_during_trading_hours_on_a_weekday() -> None:
    settings = Settings()
    # 2026-01-01 is a Thursday.
    assert is_market_open(settings, now=_at(2026, 1, 1, 11, 0)) is True


def test_closed_before_open() -> None:
    settings = Settings()
    assert is_market_open(settings, now=_at(2026, 1, 1, 9, 0)) is False


def test_closed_after_close() -> None:
    settings = Settings()
    assert is_market_open(settings, now=_at(2026, 1, 1, 16, 0)) is False


def test_closed_on_weekend() -> None:
    settings = Settings()
    # 2026-01-03 is a Saturday.
    assert is_market_open(settings, now=_at(2026, 1, 3, 11, 0)) is False


def test_respects_configured_hours() -> None:
    settings = Settings(MARKET_OPEN_TIME="10:00", MARKET_CLOSE_TIME="14:00")
    assert is_market_open(settings, now=_at(2026, 1, 1, 9, 30)) is False
    assert is_market_open(settings, now=_at(2026, 1, 1, 12, 0)) is True
