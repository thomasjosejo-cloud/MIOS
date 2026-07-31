"""Consistency Checker.

A pre-publish validator that cross-checks the engine's conclusions against each
other before the dashboard shows them. It never changes a decision — it only
flags any pair of conclusions that cannot both be true, so contradictions are
surfaced (logged) rather than silently published.

With market control now sourced from one canonical `MarketBias`, the dominance/
context/qualification/narrative agreement is guaranteed by construction; these
checks are the safety net that proves it every poll and catches any future
regression or structure-vs-options tension.
"""

from mios.schemas.dashboard import MarketDominance, MarketNarrative
from mios.schemas.market import (
    ControllingSide,
    MarketBias,
    MarketContext,
    OptionType,
    StructurePattern,
    StructureState,
    TradeQualification,
)

_TONE_FOR_SIDE = {
    ControllingSide.BULLS: "bullish",
    ControllingSide.BEARS: "bearish",
    ControllingSide.NEUTRAL: "neutral",
}


def check(
    *,
    bias: MarketBias,
    context: MarketContext,
    dominance: MarketDominance,
    structure: StructureState,
    qualification: TradeQualification,
    narrative: MarketNarrative,
) -> list[str]:
    """Return a list of contradiction messages; empty means fully consistent."""
    warnings: list[str] = []

    # 1. All three control readings must be the one canonical value.
    if context.controlling_side is not bias.controlling_side:
        warnings.append(
            f"Context control ({context.controlling_side.value}) != canonical "
            f"bias ({bias.controlling_side.value})."
        )
    if dominance.control is not bias.controlling_side:
        warnings.append(
            f"Dominance control ({dominance.control.value}) != canonical bias "
            f"({bias.controlling_side.value})."
        )

    # 2. Narrative tone must match the canonical control.
    expected_tone = _TONE_FOR_SIDE[bias.controlling_side]
    if narrative.tone != expected_tone:
        warnings.append(
            f"Narrative tone ({narrative.tone}) != canonical control ({expected_tone})."
        )

    # 3. Bias scores must actually support the stated control.
    if (
        bias.controlling_side is ControllingSide.BULLS
        and bias.bull_score <= bias.bear_score
    ):
        warnings.append(
            f"Control is BULLS but bull score {bias.bull_score:,.0f} does not "
            f"exceed bear score {bias.bear_score:,.0f}."
        )
    if (
        bias.controlling_side is ControllingSide.BEARS
        and bias.bear_score <= bias.bull_score
    ):
        warnings.append(
            f"Control is BEARS but bear score {bias.bear_score:,.0f} does not "
            f"exceed bull score {bias.bull_score:,.0f}."
        )

    # 4. A qualified trade must not contradict its own gates or the control.
    if qualification.qualified:
        if qualification.failed_gates:
            mandatory_failed = any(
                g.mandatory for g in qualification.gates if not g.passed
            )
            if mandatory_failed:
                warnings.append("Trade is qualified while a mandatory gate failed.")
        if (
            qualification.option_type is not None
            and _direction_matches(qualification, bias) is False
        ):
            warnings.append(
                f"Qualified {qualification.option_type.value} trade contradicts "
                f"canonical control ({bias.controlling_side.value})."
            )

    # 5. A confirmed breakout/breakdown with no controlling side is worth a flag:
    #    price broke a level but options positioning shows no conviction. Not a
    #    hard error, but the narrative should not imply a directional breakout.
    broke = structure.pattern in (StructurePattern.BREAKOUT, StructurePattern.BREAKDOWN)
    if broke and bias.controlling_side is ControllingSide.NEUTRAL:
        warnings.append(
            f"Structure shows {structure.pattern.value} but options positioning "
            "is neutral (no side in control)."
        )

    return warnings


def _direction_matches(qualification: TradeQualification, bias: MarketBias) -> bool:
    """Whether a qualified CE/PE trade points the same way as canonical control."""
    if qualification.option_type is OptionType.CE:
        return bias.controlling_side is ControllingSide.BULLS
    return bias.controlling_side is ControllingSide.BEARS
