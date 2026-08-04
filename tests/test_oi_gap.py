"""Tests for opening-gap classification and session-open capture."""

import datetime as dt
from decimal import Decimal

import pytest

from mios.schemas.market import GapClassification
from mios.services.options_intel.engine import _capture_session_open
from mios.services.options_intel.gap import classify_gap
from mios.services.options_intel.store import EngineStore

PREV_CLOSE = Decimal("25000")


def _open_for_gap(gap_pct: float) -> Decimal:
    """Return a session-open price that gaps exactly `gap_pct` from PREV_CLOSE."""
    return PREV_CLOSE * (Decimal(1) + Decimal(str(gap_pct)) / Decimal(100))


# --- classify_gap: threshold boundaries --------------------------------------


@pytest.mark.parametrize(
    ("gap_pct", "expected"),
    [
        (0.0, GapClassification.FLAT),
        (0.05, GapClassification.FLAT),
        (-0.05, GapClassification.FLAT),
        (0.099, GapClassification.FLAT),
        (0.1, GapClassification.GAP_UP_MARGINAL),  # 0.1% is marginal, not flat
        (-0.1, GapClassification.GAP_DOWN_MARGINAL),
        (0.3, GapClassification.GAP_UP_MARGINAL),
        (-0.3, GapClassification.GAP_DOWN_MARGINAL),
        (0.499, GapClassification.GAP_UP_MARGINAL),
        (0.5, GapClassification.GAP_UP),  # 0.5% is a full gap
        (-0.5, GapClassification.GAP_DOWN),
        (1.2, GapClassification.GAP_UP),
        (-1.2, GapClassification.GAP_DOWN),
    ],
)
def test_classify_gap_matches_specified_thresholds(
    gap_pct: float, expected: GapClassification
) -> None:
    classification, reported = classify_gap(_open_for_gap(gap_pct), PREV_CLOSE)

    assert classification is expected
    assert reported == pytest.approx(gap_pct, abs=0.01)


def test_classify_gap_reports_signed_percentage() -> None:
    up, up_pct = classify_gap(Decimal("25150"), Decimal("25000"))
    down, down_pct = classify_gap(Decimal("24850"), Decimal("25000"))

    assert up is GapClassification.GAP_UP and up_pct == 0.6
    assert down is GapClassification.GAP_DOWN and down_pct == -0.6


@pytest.mark.parametrize(
    ("session_open", "prev_close"),
    [
        (None, Decimal("25000")),
        (Decimal("25000"), None),
        (Decimal("25000"), Decimal("0")),
    ],
)
def test_classify_gap_is_none_when_uncomputable(
    session_open: Decimal | None, prev_close: Decimal | None
) -> None:
    assert classify_gap(session_open, prev_close) == (None, None)


# --- _capture_session_open: latch-once, reset-per-day ------------------------


def test_session_open_captured_on_first_open_poll() -> None:
    store = EngineStore()
    today = dt.date(2026, 8, 4)

    _capture_session_open(
        store, Decimal("25100"), market_open=True, local_date=today
    )

    assert store.session_open == Decimal("25100")
    assert store.session_date == today


def test_session_open_is_static_across_later_polls() -> None:
    store = EngineStore()
    today = dt.date(2026, 8, 4)

    _capture_session_open(store, Decimal("25100"), market_open=True, local_date=today)
    # Spot drifts through the session; the captured open must not move.
    _capture_session_open(store, Decimal("25250"), market_open=True, local_date=today)

    assert store.session_open == Decimal("25100")


def test_session_open_not_captured_while_market_closed() -> None:
    store = EngineStore()
    today = dt.date(2026, 8, 4)

    _capture_session_open(store, Decimal("25100"), market_open=False, local_date=today)

    assert store.session_open is None
    assert store.session_date == today  # the day is tracked even before open


def test_session_open_resets_on_a_new_trading_day() -> None:
    store = EngineStore()
    day_one = dt.date(2026, 8, 4)
    day_two = dt.date(2026, 8, 5)

    _capture_session_open(store, Decimal("25100"), market_open=True, local_date=day_one)
    # New session: the prior open is cleared, then re-latched at the new open.
    _capture_session_open(store, Decimal("25400"), market_open=True, local_date=day_two)

    assert store.session_open == Decimal("25400")
    assert store.session_date == day_two
