"""Decision-centric presentation helpers.

Turns the engine's existing outputs into the plain-language market narrative and
the market-dominance view the dashboard shows. This is presentation only: it
reads Classification, Context, CE/PE, Structure, Momentum, and Qualification
results and never performs any market calculation of its own.
"""

from decimal import Decimal

from mios.schemas.dashboard import MarketDominance, MarketNarrative
from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    MarketBias,
    MarketContext,
    MomentumReport,
    MomentumState,
    OptionType,
    StructurePattern,
    StructureState,
    TradeQualification,
)

_STRUCTURE_PHRASE = {
    StructurePattern.BREAKOUT: "breaking out",
    StructurePattern.BREAKDOWN: "breaking down",
    StructurePattern.PULLBACK: "pulling back",
    StructurePattern.RANGE: "inside a range",
}


def build_dominance(
    bias: MarketBias,
    classifications: list[ClassificationResult],
    *,
    previous_control: ControllingSide | None,
) -> MarketDominance:
    """Project the canonical bias into the dashboard's dominance view.

    Control and CE/PE dominance come straight from the canonical `bias`, so this
    card can never disagree with the Context card or the Narrative. The
    buyers/writers split is a separate *participant* axis — how much of the
    fresh positioning is buying versus writing — not a bull/bear reading.
    """
    control = bias.controlling_side

    buyers = sum(
        1 for c in classifications if c.classification is Classification.LONG_BUILDUP
    )
    writers = sum(
        1 for c in classifications if c.classification is Classification.SHORT_BUILDUP
    )
    total = buyers + writers
    buyers_pct = round(buyers / total * 100) if total else 50
    writers_pct = 100 - buyers_pct

    if control is ControllingSide.BULLS:
        ce_dom, pe_dom = "Strong", "Weak"
    elif control is ControllingSide.BEARS:
        ce_dom, pe_dom = "Weak", "Strong"
    else:
        ce_dom, pe_dom = "Balanced", "Balanced"

    to_label = _control_label(control)
    if previous_control is not None and previous_control is not control:
        from_label = _control_label(previous_control)
    else:
        from_label = to_label

    return MarketDominance(
        control=control,
        buyers_pct=buyers_pct,
        writers_pct=writers_pct,
        ce_dominance=ce_dom,
        pe_dominance=pe_dom,
        control_shift_from=from_label,
        control_shift_to=to_label,
    )


def build_narrative(
    classifications: list[ClassificationResult],
    context: MarketContext,
    structure: StructureState,
    momentum: MomentumReport,
    qualification: TradeQualification,
    *,
    spot: Decimal,
) -> MarketNarrative:
    """Build the plain-language market story and 'what is happening now' lines."""
    control = context.controlling_side
    tone = (
        "bullish"
        if control is ControllingSide.BULLS
        else "bearish"
        if control is ControllingSide.BEARS
        else "neutral"
    )
    statements = _statements(
        classifications, context, structure, momentum, qualification
    )
    headline = _headline(
        classifications, context, structure, qualification, tone, spot=spot
    )
    return MarketNarrative(tone=tone, headline=headline, statements=statements)


# --- internals ---------------------------------------------------------------


def _statements(
    classifications: list[ClassificationResult],
    context: MarketContext,
    structure: StructureState,
    momentum: MomentumReport,
    qualification: TradeQualification,
) -> list[str]:
    lines: list[str] = []

    if context.controlling_side is ControllingSide.BULLS:
        lines.append("Bulls are in control.")
    elif context.controlling_side is ControllingSide.BEARS:
        lines.append("Bears are in control.")
    else:
        lines.append("Neither side is in control.")

    if context.dominant_participant.value == "buyers":
        lines.append("Buyer participation increasing.")
    elif context.dominant_participant.value == "writers":
        lines.append("Writer participation increasing.")

    if _has(classifications, OptionType.CE, Classification.SHORT_COVERING):
        lines.append("Call writers are weakening.")
    if _has(classifications, OptionType.PE, Classification.SHORT_COVERING):
        lines.append("Put writers are weakening.")

    if momentum.state is MomentumState.INCREASING:
        lines.append("Momentum is increasing.")
    elif momentum.state is MomentumState.DECREASING:
        lines.append("Momentum is decreasing.")
    else:
        lines.append("Momentum is neutral.")

    lines.append(f"Price is {_STRUCTURE_PHRASE[structure.pattern]}.")

    if qualification.qualified:
        lines.append("Trade qualified.")
    elif qualification.best_candidate is not None:
        lines.append("Trade quality improving.")

    return lines


def _headline(
    classifications: list[ClassificationResult],
    context: MarketContext,
    structure: StructureState,
    qualification: TradeQualification,
    tone: str,
    *,
    spot: Decimal,
) -> str:
    emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}[tone]

    if context.controlling_side is ControllingSide.BULLS:
        opening = "Bulls are gradually taking control."
        fresh = _fresh_strikes(
            classifications, OptionType.CE, Classification.LONG_BUILDUP
        )
        activity = f"Fresh call buying is visible at {fresh}." if fresh else ""
    elif context.controlling_side is ControllingSide.BEARS:
        opening = "Bears are adding short positions."
        fresh = _fresh_strikes(
            classifications, OptionType.PE, Classification.LONG_BUILDUP
        )
        activity = f"Fresh put buying is visible at {fresh}." if fresh else ""
    else:
        opening = "Neither side has taken control."
        activity = ""

    structure_bit = f"The underlying is {_STRUCTURE_PHRASE[structure.pattern]}"

    if qualification.qualified and qualification.strike is not None:
        closing = (
            f", and MIOS has qualified {qualification.strike} "
            f"{qualification.option_type.value if qualification.option_type else ''}."
        )
    elif qualification.best_candidate is not None:
        bc = qualification.best_candidate
        closing = (
            f", so MIOS is watching {bc.strike} {bc.option_type.value} and waiting "
            "for price confirmation before qualifying a trade."
        )
    else:
        closing = ", so MIOS is standing aside until clearer signals appear."

    parts = [f"{emoji} {opening}", activity, f"{structure_bit}{closing}"]
    return " ".join(part for part in parts if part)


def _has(
    classifications: list[ClassificationResult],
    option_type: OptionType,
    classification: Classification,
) -> bool:
    return any(
        c.option_type is option_type and c.classification is classification
        for c in classifications
    )


def _fresh_strikes(
    classifications: list[ClassificationResult],
    option_type: OptionType,
    classification: Classification,
) -> str:
    strikes = sorted(
        {
            c.strike
            for c in classifications
            if c.option_type is option_type and c.classification is classification
        }
    )
    return " and ".join(str(s) for s in strikes[:2])


def _control_label(control: ControllingSide) -> str:
    return {
        ControllingSide.BULLS: "Bullish",
        ControllingSide.BEARS: "Bearish",
        ControllingSide.NEUTRAL: "Neutral",
    }[control]
