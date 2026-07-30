"""Tests for the Structure and Momentum engines."""

from collections.abc import Callable

from mios.schemas.market import (
    Candle,
    MomentumState,
    StructurePattern,
    TrendDirection,
)
from mios.services.options_intel import momentum, structure

CandleFactory = Callable[[list[float]], list[Candle]]


def test_uptrend_is_detected_from_hh_hl(
    make_candles: CandleFactory, zigzag_uptrend_closes: list[float]
) -> None:
    result = structure.analyze(make_candles(zigzag_uptrend_closes), swing_lookback=2)

    assert result.trend is TrendDirection.UPTREND
    assert result.immediate_support is not None
    assert result.immediate_resistance is not None
    assert any("swing high" in item.lower() for item in result.evidence)


def test_breakout_when_close_exceeds_resistance(
    make_candles: CandleFactory, zigzag_uptrend_closes: list[float]
) -> None:
    # The series ends by pushing to a new high above the prior swing high.
    result = structure.analyze(make_candles(zigzag_uptrend_closes), swing_lookback=2)

    assert result.pattern in (StructurePattern.BREAKOUT, StructurePattern.PULLBACK)


def test_insufficient_history_is_reported_not_crashed(
    make_candles: CandleFactory,
) -> None:
    result = structure.analyze(make_candles([100.0, 101.0]), swing_lookback=2)

    assert result.trend is TrendDirection.SIDEWAYS
    assert result.pattern is StructurePattern.RANGE
    assert any("insufficient" in item.lower() for item in result.evidence)


def test_plateau_produces_no_spurious_swings() -> None:
    # A perfectly flat series has no strict local extrema in any window, so the
    # engine must report no swings rather than flagging every tied candle.
    import datetime as dt
    from decimal import Decimal

    base = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    flat_candles = [
        Candle(
            symbol="NSE:NIFTY50-INDEX",
            timestamp=base + dt.timedelta(minutes=5 * i),
            open=Decimal(100),
            high=Decimal(100),
            low=Decimal(100),
            close=Decimal(100),
            volume=1000,
        )
        for i in range(15)
    ]

    flat = structure.analyze(flat_candles, swing_lookback=2)

    assert flat.swing_high is None
    assert flat.swing_low is None


def test_momentum_increasing_when_recent_slope_steepens(
    make_candles: CandleFactory,
) -> None:
    # 12 gentle candles then 5 steep ones, so the recent 5-candle window is far
    # steeper than the prior 5-candle window (which sits in the gentle stretch).
    gentle = [100.0 + 0.3 * i for i in range(12)]
    steep = [gentle[-1] + 4.0 * (k + 1) for k in range(5)]
    candles = make_candles(gentle + steep)
    struct = structure.analyze(candles, swing_lookback=2)

    report = momentum.analyze(candles, struct, lookback=5, acceleration_threshold=0.2)

    assert report.state is MomentumState.INCREASING


def test_momentum_neutral_on_insufficient_history(make_candles: CandleFactory) -> None:
    report = momentum.analyze(
        make_candles([100.0, 101.0, 102.0]),
        structure.analyze(make_candles([100.0, 101.0, 102.0]), swing_lookback=2),
        lookback=5,
        acceleration_threshold=0.2,
    )

    assert report.state is MomentumState.NEUTRAL
