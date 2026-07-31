"""Context Engine.

Synthesizes the CE/PE, Structure, and Momentum engines' outputs into a single,
evidence-backed explanation: who is controlling the market, why, what changed,
and whether the options activity and price structure agree or contradict each
other. Every statement traces back to a specific, already-computed fact from
an upstream engine — nothing here is inferred beyond that.
"""

from decimal import Decimal

from mios.schemas.market import (
    CePeComparison,
    Classification,
    ClassificationResult,
    ControllingSide,
    DominantParticipant,
    MarketBias,
    MarketContext,
    MomentumReport,
    MomentumState,
    OptionType,
    StructureState,
    TrendDirection,
)


def build_context(
    cepe: CePeComparison,
    structure: StructureState,
    momentum: MomentumReport,
    classifications: list[ClassificationResult],
    bias: MarketBias,
    *,
    spot: Decimal,
) -> MarketContext:
    """Build the synthesized market context from upstream engine outputs.

    Market control comes straight from the canonical Bias Engine (`bias`), so
    Context, Dominance, Qualification, and the Narrative always agree on who is
    in control. Structure then either validates or contradicts that control; it
    no longer decides it.
    """
    pe_writing = _strikes(
        classifications, OptionType.PE, Classification.SHORT_BUILDUP, spot, above=False
    )
    ce_buying = _strikes(
        classifications, OptionType.CE, Classification.LONG_BUILDUP, spot, above=True
    )
    ce_writing = _strikes(
        classifications, OptionType.CE, Classification.SHORT_BUILDUP, spot, above=True
    )
    pe_buying = _strikes(
        classifications, OptionType.PE, Classification.LONG_BUILDUP, spot, above=False
    )

    controlling_side = bias.controlling_side
    dominant_participant = _dominant_participant(classifications)

    structure_validates_options = (
        controlling_side is ControllingSide.BULLS
        and structure.trend is TrendDirection.UPTREND
    ) or (
        controlling_side is ControllingSide.BEARS
        and structure.trend is TrendDirection.DOWNTREND
    )
    contradiction = _contradiction(controlling_side, structure.trend)

    statements = _statements(
        pe_writing,
        ce_buying,
        ce_writing,
        pe_buying,
        structure,
        momentum,
        controlling_side,
        contradiction,
    )
    evidence = [*bias.evidence, *cepe.evidence, *structure.evidence, *momentum.evidence]

    return MarketContext(
        controlling_side=controlling_side,
        dominant_participant=dominant_participant,
        momentum=momentum.state,
        momentum_strengthening=momentum.state is MomentumState.INCREASING,
        momentum_weakening=momentum.state is MomentumState.DECREASING,
        structure_trend=structure.trend,
        structure_validates_options=structure_validates_options,
        contradiction=contradiction,
        immediate_support=structure.immediate_support,
        immediate_resistance=structure.immediate_resistance,
        statements=statements,
        evidence=evidence,
    )


def _strikes(
    classifications: list[ClassificationResult],
    option_type: OptionType,
    classification: Classification,
    spot: Decimal,
    *,
    above: bool,
) -> list[Decimal]:
    """Strikes matching the option type and classification, on one side of spot."""
    return sorted(
        c.strike
        for c in classifications
        if c.option_type is option_type
        and c.classification is classification
        and ((c.strike >= spot) if above else (c.strike <= spot))
    )


def _dominant_participant(
    classifications: list[ClassificationResult],
) -> DominantParticipant:
    """Determine whether fresh buying or fresh writing is more prevalent."""
    buyer_driven = sum(
        1 for c in classifications if c.classification is Classification.LONG_BUILDUP
    )
    writer_driven = sum(
        1 for c in classifications if c.classification is Classification.SHORT_BUILDUP
    )
    if buyer_driven > writer_driven:
        return DominantParticipant.BUYERS
    if writer_driven > buyer_driven:
        return DominantParticipant.WRITERS
    return DominantParticipant.BALANCED


def _contradiction(
    controlling_side: ControllingSide, trend: TrendDirection
) -> str | None:
    """Return a factual description of any options-vs-price contradiction."""
    if controlling_side is ControllingSide.BULLS and trend is TrendDirection.DOWNTREND:
        return (
            "Options activity is bullish (put writing / call buying) but price "
            "structure shows a downtrend (LH-LL)."
        )
    if controlling_side is ControllingSide.BEARS and trend is TrendDirection.UPTREND:
        return (
            "Options activity is bearish (call writing / put buying) but price "
            "structure shows an uptrend (HH-HL)."
        )
    return None


def _statements(
    pe_writing: list[Decimal],
    ce_buying: list[Decimal],
    ce_writing: list[Decimal],
    pe_buying: list[Decimal],
    structure: StructureState,
    momentum: MomentumReport,
    controlling_side: ControllingSide,
    contradiction: str | None,
) -> list[str]:
    """Build the human-readable, evidence-backed narrative lines."""
    statements: list[str] = []

    if pe_writing:
        statements.append(f"Fresh Put Writing observed at {_join(pe_writing)}.")
    if ce_buying:
        statements.append(f"Aggressive Call Buying at {_join(ce_buying)}.")
    if ce_writing:
        statements.append(f"Fresh Call Writing observed at {_join(ce_writing)}.")
    if pe_buying:
        statements.append(f"Aggressive Put Buying at {_join(pe_buying)}.")

    statements.append(_structure_statement(structure.trend))
    statements.append(f"Momentum {momentum.state.value}.")

    if controlling_side is ControllingSide.NEUTRAL:
        statements.append("No dominant side currently controls the market.")
    else:
        statements.append(
            f"{controlling_side.value.capitalize()} currently control the market."
        )

    if contradiction:
        statements.append(contradiction)

    return statements


def _structure_statement(trend: TrendDirection) -> str:
    if trend is TrendDirection.UPTREND:
        return "Price maintaining HH-HL."
    if trend is TrendDirection.DOWNTREND:
        return "Price showing LH-LL."
    return "Price structure is sideways with no defined trend."


def _join(strikes: list[Decimal]) -> str:
    return ", ".join(str(strike) for strike in strikes)
