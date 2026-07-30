"""Options Radar: the seven ranked activity views.

Four lists rank a level (current volume) and can include a strike's first
observation; the other three rank a change or velocity and require a prior
observation to exist.
"""

from collections.abc import Callable
from decimal import Decimal

from mios.schemas.market import OptionType, RadarReport, StrikeActivity, StrikeState


def build_radar(states: list[StrikeState], *, top_n: int) -> RadarReport:
    """Build all seven ranked radar views from the current strike states."""
    with_deltas = [state for state in states if not state.is_first_observation]
    ce = [state for state in with_deltas if state.option_type is OptionType.CE]
    pe = [state for state in with_deltas if state.option_type is OptionType.PE]

    return RadarReport(
        top_ce_activity=_rank(ce, top_n, metric="oi_velocity_abs", value=_abs_velocity),
        top_pe_activity=_rank(pe, top_n, metric="oi_velocity_abs", value=_abs_velocity),
        highest_oi_addition=_rank(
            with_deltas, top_n, metric="oi_change", value=lambda s: float(s.oi_change)
        ),
        highest_oi_reduction=_rank(
            with_deltas,
            top_n,
            metric="oi_change",
            value=lambda s: -float(s.oi_change),
            display=lambda s: float(s.oi_change),
        ),
        highest_volume=_rank(
            states, top_n, metric="volume", value=lambda s: float(s.current_volume)
        ),
        highest_premium_expansion=_rank(
            with_deltas,
            top_n,
            metric="premium_change_pct",
            value=lambda s: s.premium_change_pct or 0.0,
        ),
        highest_oi_velocity=_rank(
            with_deltas, top_n, metric="oi_velocity_abs", value=_abs_velocity
        ),
    )


def _abs_velocity(state: StrikeState) -> float:
    return abs(state.oi_velocity_per_min or 0.0)


def _rank(
    states: list[StrikeState],
    top_n: int,
    *,
    metric: str,
    value: Callable[[StrikeState], float],
    display: Callable[[StrikeState], float] | None = None,
) -> list[StrikeActivity]:
    """Rank states by `value` descending and return the top `top_n` as radar entries."""
    ranked = sorted(states, key=value, reverse=True)[:top_n]
    shown = display or value
    return [
        StrikeActivity(
            strike=state.strike,
            option_type=state.option_type,
            metric=metric,
            value=Decimal(str(round(shown(state), 4))),
        )
        for state in ranked
    ]
