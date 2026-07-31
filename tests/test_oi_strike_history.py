"""Unit tests for the Strike Evolution history read (backend %-derivation)."""

import datetime as dt
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from mios.schemas.market import Classification, OptionType
from mios.services.options_intel import snapshot_repository


def _row(
    captured: dt.datetime, oi: int, oi_change: int, prem: str, prem_change: str
) -> SimpleNamespace:
    return SimpleNamespace(
        captured_at=captured,
        oi=oi,
        oi_change=oi_change,
        premium=Decimal(prem),
        premium_change=Decimal(prem_change),
        volume=1000,
        volume_change=100,
        classification=Classification.SHORT_BUILDUP,
    )


def _session_returning(rows: list[SimpleNamespace]) -> MagicMock:
    """Build a mock AsyncSession whose execute() yields the given ORM rows."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    return session


async def test_history_is_oldest_first_with_derived_percentages() -> None:
    t0 = dt.datetime(2026, 1, 1, 10, 0, tzinfo=dt.UTC)
    # Repository queries newest-first; it must reverse to oldest-first.
    newest_first = [
        _row(
            t0 + dt.timedelta(minutes=2),
            oi=1500,
            oi_change=500,
            prem="80",
            prem_change="-20",
        ),
        _row(
            t0 + dt.timedelta(minutes=1),
            oi=1000,
            oi_change=400,
            prem="100",
            prem_change="-10",
        ),
    ]
    session = _session_returning(newest_first)

    history = await snapshot_repository.load_strike_history(
        session,
        symbol="NSE:NIFTY50-INDEX",
        strike=Decimal(24400),
        option_type=OptionType.PE,
        limit=100,
    )

    assert history.strike == Decimal(24400)
    assert history.option_type is OptionType.PE
    assert [p.captured_at for p in history.points] == [
        t0 + dt.timedelta(minutes=1),
        t0 + dt.timedelta(minutes=2),
    ]
    # %ΔOI derived from stored current + delta: previous = oi - oi_change.
    # Point 1: 400 / (1000-400) = 66.67%. Point 2: 500 / (1500-500) = 50.0%.
    assert history.points[0].oi_change_pct == pytest.approx(66.67, abs=0.01)
    assert history.points[1].oi_change_pct == pytest.approx(50.0)
    # Premium % derived similarly (negative for put writing).
    assert history.points[0].premium_change_pct == pytest.approx(-9.09, abs=0.01)


async def test_empty_history_returns_empty_series() -> None:
    session = _session_returning([])

    history = await snapshot_repository.load_strike_history(
        session,
        symbol="NSE:NIFTY50-INDEX",
        strike=Decimal(24400),
        option_type=OptionType.CE,
        limit=100,
    )

    assert history.points == []


def test_pct_helper_handles_zero_previous() -> None:
    # previous = current - change == 0 -> undefined percentage, not a crash.
    assert snapshot_repository._pct(Decimal(500), Decimal(500)) is None
    assert snapshot_repository._pct(Decimal(50), Decimal(150)) == pytest.approx(50.0)
