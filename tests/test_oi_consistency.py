"""Sprint 11 tests for the pre-publish Consistency Checker."""

from decimal import Decimal

from mios.schemas.dashboard import MarketDominance, MarketNarrative
from mios.schemas.market import (
    ConfidenceBand,
    ControllingSide,
    DominantParticipant,
    MarketBias,
    MarketContext,
    MomentumState,
    OptionType,
    StructurePattern,
    StructureState,
    TradeDecision,
    TradeQualification,
    TrendDirection,
)
from mios.services.options_intel import consistency


def _bias(control: ControllingSide, *, bull: float, bear: float) -> MarketBias:
    return MarketBias(
        controlling_side=control,
        bull_score=bull,
        bear_score=bear,
        net_score=bull - bear,
        contributions=[],
        evidence=["bias"],
    )


def _context(control: ControllingSide) -> MarketContext:
    return MarketContext(
        controlling_side=control,
        dominant_participant=DominantParticipant.BUYERS,
        momentum=MomentumState.INCREASING,
        momentum_strengthening=True,
        momentum_weakening=False,
        structure_trend=TrendDirection.UPTREND,
        structure_validates_options=True,
        contradiction=None,
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        structure_pattern=StructurePattern.RANGE,
        swing_high=Decimal(24800),
        swing_low=Decimal(24600),
        gap_classification=None,
        gap_pct=None,
        statements=["s"],
        evidence=["e"],
    )


def _dominance(control: ControllingSide) -> MarketDominance:
    return MarketDominance(
        control=control,
        buyers_pct=60,
        writers_pct=40,
        ce_dominance="Strong",
        pe_dominance="Weak",
        control_shift_from="Neutral",
        control_shift_to="Bullish",
    )


def _structure(pattern: StructurePattern) -> StructureState:
    return StructureState(
        swing_high=Decimal(24800),
        swing_low=Decimal(24600),
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        pattern=pattern,
        trend=TrendDirection.UPTREND,
        evidence=["s"],
    )


def _narrative(tone: str) -> MarketNarrative:
    return MarketNarrative(tone=tone, headline="h", statements=["x"])


def _qualification(*, qualified: bool, ot: OptionType | None) -> TradeQualification:
    return TradeQualification(
        decision=TradeDecision.BUY_CE if qualified else TradeDecision.NO_TRADE,
        qualified=qualified,
        strike=Decimal(24700) if qualified else None,
        option_type=ot,
        classification=None,
        confidence=100 if qualified else 40,
        band=ConfidenceBand.VERY_HIGH if qualified else ConfidenceBand.LOW,
        gates=[],
        failed_gates=[],
        reasons=[],
        best_candidate=None,
    )


def test_all_aligned_produces_no_warnings() -> None:
    warnings = consistency.check(
        bias=_bias(ControllingSide.BULLS, bull=100, bear=10),
        context=_context(ControllingSide.BULLS),
        dominance=_dominance(ControllingSide.BULLS),
        structure=_structure(StructurePattern.BREAKOUT),
        qualification=_qualification(qualified=True, ot=OptionType.CE),
        narrative=_narrative("bullish"),
    )
    assert warnings == []


def test_dominance_disagreeing_with_bias_is_flagged() -> None:
    # The exact Sprint 11 defect: bias bullish, dominance bearish.
    warnings = consistency.check(
        bias=_bias(ControllingSide.BULLS, bull=100, bear=10),
        context=_context(ControllingSide.BULLS),
        dominance=_dominance(ControllingSide.BEARS),
        structure=_structure(StructurePattern.RANGE),
        qualification=_qualification(qualified=False, ot=None),
        narrative=_narrative("bullish"),
    )
    assert any("Dominance control" in w for w in warnings)


def test_narrative_tone_mismatch_is_flagged() -> None:
    warnings = consistency.check(
        bias=_bias(ControllingSide.BULLS, bull=100, bear=10),
        context=_context(ControllingSide.BULLS),
        dominance=_dominance(ControllingSide.BULLS),
        structure=_structure(StructurePattern.RANGE),
        qualification=_qualification(qualified=False, ot=None),
        narrative=_narrative("bearish"),
    )
    assert any("Narrative tone" in w for w in warnings)


def test_breakout_with_neutral_control_is_flagged() -> None:
    warnings = consistency.check(
        bias=_bias(ControllingSide.NEUTRAL, bull=0, bear=0),
        context=_context(ControllingSide.NEUTRAL),
        dominance=_dominance(ControllingSide.NEUTRAL),
        structure=_structure(StructurePattern.BREAKOUT),
        qualification=_qualification(qualified=False, ot=None),
        narrative=_narrative("neutral"),
    )
    assert any("neutral" in w.lower() and "breakout" in w.lower() for w in warnings)


def test_qualified_trade_against_control_is_flagged() -> None:
    warnings = consistency.check(
        bias=_bias(ControllingSide.BULLS, bull=100, bear=10),
        context=_context(ControllingSide.BULLS),
        dominance=_dominance(ControllingSide.BULLS),
        structure=_structure(StructurePattern.BREAKOUT),
        # Qualified PE trade while control is bulls — contradiction.
        qualification=_qualification(qualified=True, ot=OptionType.PE),
        narrative=_narrative("bullish"),
    )
    assert any("contradicts canonical control" in w for w in warnings)
