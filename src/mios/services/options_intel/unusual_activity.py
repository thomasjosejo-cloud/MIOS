"""Unusual Activity Engine.

Flags strikes whose change in any single metric crosses a configured
threshold. A strike with no prior observation is never flagged — there is no
change to measure yet, so including it would be noise, not signal.
"""

from mios.schemas.market import StrikeState, UnusualActivity


def detect(
    states: list[StrikeState],
    *,
    oi_change_pct: float,
    volume_change_pct: float,
    premium_change_pct: float,
    oi_velocity_per_min: float,
) -> list[UnusualActivity]:
    """Return every strike whose activity crossed at least one threshold."""
    results: list[UnusualActivity] = []

    for state in states:
        if state.is_first_observation:
            continue

        triggers: list[str] = []
        evidence: list[str] = []

        if (
            state.oi_change_pct is not None
            and abs(state.oi_change_pct) >= oi_change_pct
        ):
            triggers.append("oi_change")
            evidence.append(
                f"OI change {state.oi_change_pct:+.1f}% "
                f"(threshold {oi_change_pct:.0f}%)"
            )

        if (
            state.volume_change_pct is not None
            and abs(state.volume_change_pct) >= volume_change_pct
        ):
            triggers.append("volume_change")
            evidence.append(
                f"Volume change {state.volume_change_pct:+.1f}% "
                f"(threshold {volume_change_pct:.0f}%)"
            )

        if (
            state.premium_change_pct is not None
            and abs(state.premium_change_pct) >= premium_change_pct
        ):
            triggers.append("premium_change")
            evidence.append(
                f"Premium change {state.premium_change_pct:+.1f}% "
                f"(threshold {premium_change_pct:.0f}%)"
            )

        if (
            state.oi_velocity_per_min is not None
            and abs(state.oi_velocity_per_min) >= oi_velocity_per_min
        ):
            triggers.append("oi_velocity")
            evidence.append(
                f"OI velocity {state.oi_velocity_per_min:+.0f}/min "
                f"(threshold {oi_velocity_per_min:.0f}/min)"
            )

        if triggers:
            results.append(
                UnusualActivity(
                    strike=state.strike,
                    option_type=state.option_type,
                    triggers=triggers,
                    evidence=evidence,
                )
            )

    return results
