"""CE vs PE Engine.

Compares net Call-side and Put-side open interest addition to determine which
side is stronger, reuses the Classification Engine's output to identify where
writers versus buyers are active, and tracks whether the stronger side has
changed since the previous poll.
"""

from mios.schemas.market import (
    CePeComparison,
    Classification,
    ClassificationResult,
    MarketSide,
    OptionType,
    StrikeState,
    UnusualActivity,
)


def compare(
    states: list[StrikeState],
    classifications: list[ClassificationResult],
    unusual: list[UnusualActivity],
    *,
    neutral_band_pct: float,
    previous: CePeComparison | None,
) -> CePeComparison:
    """Compare CE and PE activity, given the current classification and OI state."""
    ce_states = [
        s
        for s in states
        if s.option_type is OptionType.CE and not s.is_first_observation
    ]
    pe_states = [
        s
        for s in states
        if s.option_type is OptionType.PE and not s.is_first_observation
    ]

    ce_net_oi = sum(s.oi_change for s in ce_states)
    pe_net_oi = sum(s.oi_change for s in pe_states)
    stronger_side = _stronger_side(ce_net_oi, pe_net_oi, neutral_band_pct)

    writer_active_strikes = sorted(
        {
            c.strike
            for c in classifications
            if c.classification is Classification.SHORT_BUILDUP
        }
    )
    buyer_active_strikes = sorted(
        {
            c.strike
            for c in classifications
            if c.classification is Classification.LONG_BUILDUP
        }
    )
    important_strikes = sorted({u.strike for u in unusual})

    control_shifting = previous is not None and previous.stronger_side != stronger_side
    shift_description = None
    if control_shifting and previous is not None:
        shift_description = (
            f"Control shifted from {previous.stronger_side.value} to "
            f"{stronger_side.value}."
        )

    evidence = [
        f"Net CE OI change: {ce_net_oi:+,}",
        f"Net PE OI change: {pe_net_oi:+,}",
    ]
    if writer_active_strikes:
        evidence.append(
            "Writer activity at strikes: "
            + ", ".join(str(strike) for strike in writer_active_strikes)
        )
    if buyer_active_strikes:
        evidence.append(
            "Buyer activity at strikes: "
            + ", ".join(str(strike) for strike in buyer_active_strikes)
        )

    return CePeComparison(
        stronger_side=stronger_side,
        writer_active_strikes=writer_active_strikes,
        buyer_active_strikes=buyer_active_strikes,
        control_shifting=control_shifting,
        shift_description=shift_description,
        important_strikes=important_strikes,
        evidence=evidence,
    )


def _stronger_side(
    ce_net_oi: int, pe_net_oi: int, neutral_band_pct: float
) -> MarketSide:
    """Determine the stronger side from net OI addition, within a neutral band."""
    larger = max(abs(ce_net_oi), abs(pe_net_oi))
    if larger == 0:
        return MarketSide.NEUTRAL

    gap_pct = abs(ce_net_oi - pe_net_oi) / larger * 100
    if gap_pct < neutral_band_pct:
        return MarketSide.NEUTRAL

    return MarketSide.CE if ce_net_oi > pe_net_oi else MarketSide.PE
