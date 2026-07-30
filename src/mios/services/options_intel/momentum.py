"""Momentum Engine.

Compares the rate of price movement over the most recent window of candles
against the window immediately before it. A larger recent slope means momentum
is accelerating (`INCREASING`); a smaller one means it is fading
(`DECREASING`). Volume and structure trend are attached as supporting
evidence, not as separate inputs to the state itself.
"""

from mios.schemas.market import Candle, MomentumReport, MomentumState, StructureState


def analyze(
    candles: list[Candle],
    structure: StructureState,
    *,
    lookback: int,
    acceleration_threshold: float,
) -> MomentumReport:
    """Determine whether price momentum is increasing, decreasing, or neutral."""
    required = 2 * lookback
    if len(candles) < required:
        return MomentumReport(
            state=MomentumState.NEUTRAL,
            evidence=[
                f"Insufficient candle history for momentum analysis "
                f"(need at least {required}, have {len(candles)})"
            ],
        )

    recent = candles[-lookback:]
    prior = candles[-2 * lookback : -lookback]

    recent_slope_pct = _slope_pct(recent)
    prior_slope_pct = _slope_pct(prior)

    if abs(recent_slope_pct) > abs(prior_slope_pct) * (1 + acceleration_threshold):
        state = MomentumState.INCREASING
    elif abs(recent_slope_pct) < abs(prior_slope_pct) * (1 - acceleration_threshold):
        state = MomentumState.DECREASING
    else:
        state = MomentumState.NEUTRAL

    recent_avg_volume = sum(c.volume for c in recent) / len(recent)
    prior_avg_volume = sum(c.volume for c in prior) / len(prior)
    volume_direction = "up" if recent_avg_volume > prior_avg_volume else "down"

    evidence = [
        f"Recent {lookback}-candle slope: {recent_slope_pct:+.2f}%",
        f"Prior {lookback}-candle slope: {prior_slope_pct:+.2f}%",
        f"Volume trending {volume_direction} "
        f"({recent_avg_volume:.0f} vs {prior_avg_volume:.0f})",
        f"Structure trend: {structure.trend.value}",
    ]

    return MomentumReport(state=state, evidence=evidence)


def _slope_pct(window: list[Candle]) -> float:
    """Percent change in close from the first to the last candle of `window`."""
    start, end = window[0].close, window[-1].close
    if start == 0:
        return 0.0
    return float((end - start) / start * 100)
