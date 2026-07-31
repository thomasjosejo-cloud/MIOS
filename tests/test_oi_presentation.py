"""Sprint 10.1 tests for the decision-centric presentation layer.

Presentation reads existing engine outputs only; these tests assert it derives
the narrative and dominance from that data and never invents values.
"""

from decimal import Decimal

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ConfidenceBand,
    ControllingSide,
    DominantParticipant,
    MarketBias,
    MarketContext,
    MomentumReport,
    MomentumState,
    OptionType,
    StructurePattern,
    StructureState,
    TradeDecision,
    TradeQualification,
    TrendDirection,
)
from mios.services.options_intel import presentation


def _classification(
    strike: int, option_type: OptionType, cls: Classification
) -> ClassificationResult:
    return ClassificationResult(
        strike=Decimal(strike),
        option_type=option_type,
        classification=cls,
        evidence=["OI ↑ 20.0%"],
        reason="reason.",
    )


def _bias(
    control: ControllingSide, *, bull: float = 0.0, bear: float = 0.0
) -> MarketBias:
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
        statements=["stmt"],
        evidence=["evidence"],
    )


def _structure() -> StructureState:
    return StructureState(
        swing_high=Decimal(24800),
        swing_low=Decimal(24600),
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        pattern=StructurePattern.RANGE,
        trend=TrendDirection.UPTREND,
        evidence=["structure"],
    )


def _qualification(*, qualified: bool) -> TradeQualification:
    return TradeQualification(
        decision=TradeDecision.BUY_CE if qualified else TradeDecision.NO_TRADE,
        qualified=qualified,
        strike=Decimal(24700) if qualified else None,
        option_type=OptionType.CE if qualified else None,
        classification=Classification.LONG_BUILDUP if qualified else None,
        confidence=100 if qualified else 70,
        band=ConfidenceBand.VERY_HIGH if qualified else ConfidenceBand.MEDIUM,
        gates=[],
        failed_gates=[],
        reasons=[],
        best_candidate=None,
    )


# --- Dominance ---------------------------------------------------------------


def test_dominance_control_comes_from_canonical_bias() -> None:
    # Control and CE/PE dominance follow the canonical bias, never raw OI.
    classifications = [
        _classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        _classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
        _classification(24650, OptionType.CE, Classification.LONG_BUILDUP),
        _classification(24600, OptionType.PE, Classification.SHORT_BUILDUP),
    ]

    dominance = presentation.build_dominance(
        _bias(ControllingSide.BULLS, bull=100), classifications, previous_control=None
    )

    assert dominance.control is ControllingSide.BULLS
    # Participant axis: 3 long build-ups (buying) vs 1 short build-up (writing).
    assert dominance.buyers_pct == 75
    assert dominance.writers_pct == 25
    assert dominance.ce_dominance == "Strong"
    assert dominance.pe_dominance == "Weak"


def test_dominance_put_writing_is_not_read_as_bearish() -> None:
    # Regression for the Sprint 11 defect: PE Short Build (put writing) is
    # bullish, so a bias-BULLS control must NOT be flipped to bears.
    classifications = [
        _classification(24300, OptionType.PE, Classification.SHORT_BUILDUP),
        _classification(24350, OptionType.PE, Classification.SHORT_BUILDUP),
    ]

    dominance = presentation.build_dominance(
        _bias(ControllingSide.BULLS, bull=660_000),
        classifications,
        previous_control=None,
    )

    assert dominance.control is ControllingSide.BULLS
    assert dominance.pe_dominance == "Weak"  # not "Strong/bearish"


def test_dominance_reports_control_shift() -> None:
    dominance = presentation.build_dominance(
        _bias(ControllingSide.BULLS, bull=100),
        [],
        previous_control=ControllingSide.NEUTRAL,
    )

    assert dominance.control_shift_from == "Neutral"
    assert dominance.control_shift_to == "Bullish"


def test_dominance_neutral_when_bias_neutral() -> None:
    dominance = presentation.build_dominance(
        _bias(ControllingSide.NEUTRAL), [], previous_control=None
    )

    assert dominance.control is ControllingSide.NEUTRAL
    assert dominance.buyers_pct == 50  # no participants → balanced default
    assert dominance.ce_dominance == "Balanced"


# --- Narrative ---------------------------------------------------------------


def test_narrative_headline_is_bullish_and_names_fresh_strikes() -> None:
    classifications = [
        _classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        _classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
    ]
    momentum = MomentumReport(state=MomentumState.INCREASING, evidence=["m"])

    narrative = presentation.build_narrative(
        classifications,
        _context(ControllingSide.BULLS),
        _structure(),
        momentum,
        _qualification(qualified=False),
        spot=Decimal(24700),
    )

    assert narrative.tone == "bullish"
    assert narrative.headline.startswith("🟢")
    assert "24700" in narrative.headline
    assert narrative.statements  # never empty


def test_narrative_neutral_when_no_side_controls() -> None:
    momentum = MomentumReport(state=MomentumState.NEUTRAL, evidence=["m"])

    narrative = presentation.build_narrative(
        [],
        _context(ControllingSide.NEUTRAL),
        _structure(),
        momentum,
        _qualification(qualified=False),
        spot=Decimal(24700),
    )

    assert narrative.tone == "neutral"
    assert narrative.headline.startswith("⚪")
    assert any("Neither side" in line for line in narrative.statements)
