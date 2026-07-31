"""Bias Engine — the single canonical read of market control.

Position labels are side-dependent: writing calls is bearish, writing puts is
bullish. This engine resolves each classified strike to its true directional
*meaning* (Sentiment) via one fixed mapping, weights it by the magnitude of the
fresh positioning (|OI change|, already computed upstream), and sums the result
into bull and bear scores. Control is then decided from those scores within the
same neutral band the rest of the system uses.

Every downstream component (Context, Dominance, Qualification, Narrative) reads
control from this one object, so they cannot contradict each other. Nothing here
uses raw OI direction alone — that was the defect this engine replaces.
"""

from decimal import Decimal

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    MarketBias,
    OptionType,
    Sentiment,
    StrikeContribution,
    StrikeState,
)

#: The canonical classification -> market-meaning table (all eight branches).
#: CE and PE map the same position label to opposite sentiment.
_SENTIMENT: dict[tuple[OptionType, Classification], Sentiment] = {
    # Calls: buying/holding calls is bullish; writing/closing them is bearish.
    (OptionType.CE, Classification.LONG_BUILDUP): Sentiment.BULLISH,
    (OptionType.CE, Classification.SHORT_COVERING): Sentiment.BULLISH,
    (OptionType.CE, Classification.SHORT_BUILDUP): Sentiment.BEARISH,
    (OptionType.CE, Classification.LONG_UNWINDING): Sentiment.BEARISH,
    # Puts: writing/closing puts is bullish; buying/holding them is bearish.
    (OptionType.PE, Classification.SHORT_BUILDUP): Sentiment.BULLISH,
    (OptionType.PE, Classification.LONG_UNWINDING): Sentiment.BULLISH,
    (OptionType.PE, Classification.LONG_BUILDUP): Sentiment.BEARISH,
    (OptionType.PE, Classification.SHORT_COVERING): Sentiment.BEARISH,
}


def sentiment_of(option_type: OptionType, classification: Classification) -> Sentiment:
    """Resolve a classified strike to its canonical bullish/bearish meaning."""
    return _SENTIMENT[(option_type, classification)]


def assess(
    classifications: list[ClassificationResult],
    strike_states: list[StrikeState],
    *,
    neutral_band_pct: float,
) -> MarketBias:
    """Compute the canonical market bias from classification-resolved sentiment."""
    oi_change_by: dict[tuple[Decimal, OptionType], int] = {
        (s.strike, s.option_type): s.oi_change for s in strike_states
    }

    contributions: list[StrikeContribution] = []
    bull_score = 0.0
    bear_score = 0.0

    for result in classifications:
        sentiment = _SENTIMENT[(result.option_type, result.classification)]
        weight = abs(oi_change_by.get((result.strike, result.option_type), 0))
        signed = float(weight if sentiment is Sentiment.BULLISH else -weight)
        if sentiment is Sentiment.BULLISH:
            bull_score += weight
        else:
            bear_score += weight
        contributions.append(
            StrikeContribution(
                strike=result.strike,
                option_type=result.option_type,
                classification=result.classification,
                sentiment=sentiment,
                weight=weight,
                signed_score=signed,
            )
        )

    controlling_side = _controlling_side(bull_score, bear_score, neutral_band_pct)
    evidence = _evidence(bull_score, bear_score, controlling_side, contributions)

    return MarketBias(
        controlling_side=controlling_side,
        bull_score=bull_score,
        bear_score=bear_score,
        net_score=bull_score - bear_score,
        contributions=contributions,
        evidence=evidence,
    )


def _controlling_side(
    bull_score: float, bear_score: float, neutral_band_pct: float
) -> ControllingSide:
    """Decide control from bull/bear scores within the shared neutral band."""
    larger = max(bull_score, bear_score)
    if larger == 0:
        return ControllingSide.NEUTRAL
    gap_pct = abs(bull_score - bear_score) / larger * 100
    if gap_pct < neutral_band_pct:
        return ControllingSide.NEUTRAL
    return ControllingSide.BULLS if bull_score > bear_score else ControllingSide.BEARS


def _evidence(
    bull_score: float,
    bear_score: float,
    controlling_side: ControllingSide,
    contributions: list[StrikeContribution],
) -> list[str]:
    """Build factual, measurable evidence lines for the bias decision."""
    bullish = [c for c in contributions if c.sentiment is Sentiment.BULLISH]
    bearish = [c for c in contributions if c.sentiment is Sentiment.BEARISH]
    evidence = [
        f"Bullish score {bull_score:,.0f} from {len(bullish)} strike(s)",
        f"Bearish score {bear_score:,.0f} from {len(bearish)} strike(s)",
        f"Net bias {bull_score - bear_score:+,.0f} => {controlling_side.value}",
    ]
    return evidence
