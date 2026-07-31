"""Sprint 10 tests for the Trade Qualification Engine's four gates.

These build engine-output schemas directly so each gate and the confidence
formula can be exercised in isolation, then assert on `qualify(...)`.
"""

import datetime as dt
from decimal import Decimal

from mios.config import Settings
from mios.schemas.market import (
    CePeComparison,
    Classification,
    ClassificationResult,
    ConfidenceBand,
    ControllingSide,
    DominantParticipant,
    GateName,
    MarketContext,
    MarketSide,
    MomentumState,
    OptionType,
    StrikeState,
    StructurePattern,
    StructureState,
    TradeDecision,
    TradeQualification,
    TrendDirection,
    UnusualActivity,
)
from mios.services.options_intel import qualification as qual

_T0 = dt.datetime(2026, 1, 1, 9, 20, tzinfo=dt.UTC)
_SPOT = Decimal(24700)


def _settings() -> Settings:
    return Settings(
        FYERS_APP_ID="x",
        FYERS_SECRET_KEY="y",
        FYERS_REDIRECT_URI="http://localhost/callback",
    )


def state(
    strike: int,
    option_type: OptionType,
    *,
    oi: int = 20_000,
    volume: int = 5_000,
    premium: float = 100.0,
) -> StrikeState:
    return StrikeState(
        strike=Decimal(strike),
        option_type=option_type,
        expiry=dt.date(2026, 1, 8),
        current_oi=oi,
        previous_oi=oi - 1,
        oi_change=1,
        oi_change_pct=20.0,
        current_premium=Decimal(str(premium)),
        previous_premium=Decimal(str(premium)),
        premium_change=Decimal(0),
        premium_change_pct=10.0,
        current_volume=volume,
        previous_volume=volume - 1,
        volume_change=1,
        volume_change_pct=30.0,
        last_updated=_T0,
        seconds_since_update=5.0,
    )


def classification(
    strike: int, option_type: OptionType, cls: Classification
) -> ClassificationResult:
    return ClassificationResult(
        strike=Decimal(strike),
        option_type=option_type,
        classification=cls,
        evidence=["OI ↑ 20.0%", "Premium ↑ 10.0%", "Volume ↑ 30.0%"],
        reason="reason.",
    )


def unusual(strike: int, option_type: OptionType) -> UnusualActivity:
    return UnusualActivity(
        strike=Decimal(strike),
        option_type=option_type,
        triggers=["oi_change", "volume_change"],
        evidence=["oi_change exceeded", "volume_change exceeded"],
    )


def structure(
    *,
    pattern: StructurePattern = StructurePattern.BREAKOUT,
    trend: TrendDirection = TrendDirection.UPTREND,
) -> StructureState:
    return StructureState(
        swing_high=Decimal(24800),
        swing_low=Decimal(24600),
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        pattern=pattern,
        trend=trend,
        evidence=["structure"],
    )


def context(
    *,
    controlling: ControllingSide = ControllingSide.BULLS,
    dominant: DominantParticipant = DominantParticipant.BUYERS,
    contradiction: str | None = None,
    validates: bool = True,
) -> MarketContext:
    return MarketContext(
        controlling_side=controlling,
        dominant_participant=dominant,
        momentum=MomentumState.INCREASING,
        momentum_strengthening=True,
        momentum_weakening=False,
        structure_trend=TrendDirection.UPTREND,
        structure_validates_options=validates,
        contradiction=contradiction,
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        statements=["stmt"],
        evidence=["evidence"],
    )


def cepe(stronger: MarketSide = MarketSide.CE) -> CePeComparison:
    return CePeComparison(
        stronger_side=stronger,
        writer_active_strikes=[],
        buyer_active_strikes=[Decimal(24700)],
        control_shifting=False,
        shift_description=None,
        important_strikes=[Decimal(24700)],
        evidence=["cepe"],
    )


def _qualify(
    classifications: list[ClassificationResult],
    unusuals: list[UnusualActivity],
    states: list[StrikeState],
    *,
    structure_: StructureState,
    context_: MarketContext,
    cepe_: CePeComparison,
) -> TradeQualification:
    return qual.qualify(
        classifications,
        unusuals,
        states,
        structure_,
        context_,
        cepe_,
        spot=_SPOT,
        settings=_settings(),
    )


# --- Happy path: all mandatory gates pass -> BUY -----------------------------


def test_all_gates_pass_qualifies_buy_ce() -> None:
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [unusual(24700, OptionType.CE)],
        [state(24700, OptionType.CE)],
        structure_=structure(),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.qualified is True
    assert result.decision is TradeDecision.BUY_CE
    assert result.strike == Decimal(24700)
    assert result.option_type is OptionType.CE
    assert result.confidence == 100  # all four gates pass (30+30+25+15)
    assert result.band is ConfidenceBand.VERY_HIGH
    assert result.failed_gates == []


# --- Gate 1: sideways/choppy market -> NO_TRADE ------------------------------


def test_sideways_market_fails_gate1_no_trade() -> None:
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [],
        [state(24700, OptionType.CE)],
        structure_=structure(
            pattern=StructurePattern.RANGE, trend=TrendDirection.SIDEWAYS
        ),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.qualified is False
    assert result.decision is TradeDecision.NO_TRADE
    assert GateName.MARKET_REGIME in result.failed_gates
    assert result.confidence == 70  # gates 2, 3, 4 pass (30+25+15)


# --- Gate 2: no participation on the controlling side -> NO_TRADE ------------


def test_no_participation_fails_gate2_no_trade() -> None:
    # Bulls control, but the only classified strike is a PE — no CE candidate.
    result = _qualify(
        [classification(24700, OptionType.PE, Classification.LONG_BUILDUP)],
        [],
        [state(24700, OptionType.PE)],
        structure_=structure(),
        context_=context(controlling=ControllingSide.BULLS),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.qualified is False
    assert GateName.OPTIONS_PARTICIPATION in result.failed_gates
    assert result.strike is None


# --- Gate 3: neither side controls -> NO_TRADE -------------------------------


def test_neutral_control_fails_gate3_no_trade() -> None:
    # Neutral control means no direction and no candidates at all.
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [],
        [state(24700, OptionType.CE)],
        structure_=structure(),
        context_=context(controlling=ControllingSide.NEUTRAL),
        cepe_=cepe(MarketSide.NEUTRAL),
    )

    assert result.qualified is False
    assert GateName.CE_PE_CONTROL in result.failed_gates
    assert GateName.OPTIONS_PARTICIPATION in result.failed_gates


# --- Gate 4 is non-blocking: fails but mandatory gates pass -> still BUY -----


def test_strike_quality_fails_but_still_qualifies() -> None:
    # A far OTM strike fails Gate 4 (too far from ATM) but the three mandatory
    # gates pass, so the trade still qualifies at reduced confidence.
    far_strike = 24700 + 50 * 9  # 9 steps from ATM (max is 8)
    result = _qualify(
        [classification(far_strike, OptionType.CE, Classification.LONG_BUILDUP)],
        [],
        [state(far_strike, OptionType.CE)],
        structure_=structure(),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.qualified is True
    assert result.decision is TradeDecision.BUY_CE
    assert GateName.STRIKE_QUALITY in result.failed_gates
    assert result.confidence == 85  # 30+30+25, Gate 4's 15 withheld
    assert result.band is ConfidenceBand.HIGH


# --- Best candidate is always populated when a candidate exists --------------


def test_best_candidate_present_during_no_trade() -> None:
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [],
        [state(24700, OptionType.CE)],
        structure_=structure(
            pattern=StructurePattern.RANGE, trend=TrendDirection.SIDEWAYS
        ),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.decision is TradeDecision.NO_TRADE
    assert result.best_candidate is not None
    assert result.best_candidate.strike == Decimal(24700)
    assert result.best_candidate.option_type is OptionType.CE


# --- Liquidity ordering: most liquid candidate leads -------------------------


def test_most_liquid_candidate_chosen() -> None:
    result = _qualify(
        [
            classification(24650, OptionType.CE, Classification.LONG_BUILDUP),
            classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        ],
        [],
        [
            state(24650, OptionType.CE, oi=10_000),
            state(24700, OptionType.CE, oi=50_000),
        ],
        structure_=structure(),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert result.strike == Decimal(24700)  # higher OI wins


# --- Evidence is factual only ------------------------------------------------


def test_reasons_are_factual_only() -> None:
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [unusual(24700, OptionType.CE)],
        [state(24700, OptionType.CE)],
        structure_=structure(),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert "Unusual activity flagged" in result.reasons
    assert "Buyers dominant" in result.reasons
    assert "Bulls control market" in result.reasons
    banned = ("guaranteed", "certain", "sure thing", "confident")
    for line in result.reasons:
        lowered = line.lower()
        assert all(word not in lowered for word in banned)


def test_unusual_flag_absent_when_no_unusual_activity() -> None:
    # Do not invent evidence: with no unusual activity, the line must not appear.
    result = _qualify(
        [classification(24700, OptionType.CE, Classification.LONG_BUILDUP)],
        [],
        [state(24700, OptionType.CE)],
        structure_=structure(),
        context_=context(),
        cepe_=cepe(MarketSide.CE),
    )

    assert "Unusual activity flagged" not in result.reasons


# --- Determinism -------------------------------------------------------------


def test_identical_input_produces_identical_output() -> None:
    def run() -> dict[str, object]:
        result = _qualify(
            [
                classification(24650, OptionType.CE, Classification.LONG_BUILDUP),
                classification(24700, OptionType.CE, Classification.SHORT_COVERING),
            ],
            [unusual(24700, OptionType.CE)],
            [state(24650, OptionType.CE), state(24700, OptionType.CE)],
            structure_=structure(),
            context_=context(),
            cepe_=cepe(MarketSide.CE),
        )
        return result.model_dump()

    assert run() == run()
