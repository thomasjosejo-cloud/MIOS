"""No-Trade Engine.

Declares NO TRADE only when multiple independent negative conditions are true
together, so a single flaky signal can never trigger it alone. Every reason is
a direct fact already computed by an upstream engine.
"""

from mios.schemas.market import (
    ControllingSide,
    MarketContext,
    MomentumReport,
    MomentumState,
    NoTradeDecision,
    StructurePattern,
    StructureState,
    TrendDirection,
)


def evaluate(
    context: MarketContext,
    structure: StructureState,
    momentum: MomentumReport,
    *,
    ce_rank: int | None,
    pe_rank: int | None,
    rank_tie_margin: int,
    min_reasons: int,
) -> NoTradeDecision:
    """Evaluate whether the current conditions call for no trade at all."""
    reasons: list[str] = []

    if ce_rank is None and pe_rank is None:
        reasons.append("No CE or PE candidate met the minimum supporting evidence.")
    elif (
        ce_rank is not None
        and pe_rank is not None
        and abs(ce_rank - pe_rank) <= rank_tie_margin
    ):
        reasons.append(
            "Conflicting CE PE positioning: both sides show comparable evidence."
        )

    if structure.trend is TrendDirection.SIDEWAYS:
        reasons.append(
            "No HH-HL or LH-LL structure; price action lacks a defined trend."
        )

    if momentum.state is MomentumState.NEUTRAL:
        reasons.append("Weak momentum: no acceleration in either direction.")

    if structure.pattern is StructurePattern.RANGE:
        reasons.append("Price is inside a range, with no breakout or breakdown.")

    if context.controlling_side is ControllingSide.NEUTRAL:
        reasons.append("No dominant side: buyers and writers are balanced.")

    no_trade = len(reasons) >= min_reasons
    return NoTradeDecision(no_trade=no_trade, reasons=reasons if no_trade else [])
