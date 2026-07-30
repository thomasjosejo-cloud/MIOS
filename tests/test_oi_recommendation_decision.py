"""Sprint 5 tests for the Recommendation Engine's ordered decision hierarchy.

These build engine-output schemas directly so each decision stage can be
exercised in isolation, then assert on `rank_candidates` / `build_report`.
"""

import datetime as dt
from decimal import Decimal

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    DominantParticipant,
    MarketContext,
    MomentumReport,
    MomentumState,
    NoTradeDecision,
    OptionType,
    StrikeState,
    StructurePattern,
    StructureState,
    TrendDirection,
    UnusualActivity,
)
from mios.services.options_intel import recommendation as rec
from mios.services.options_intel.recommendation import CandidateRanking

_T0 = dt.datetime(2026, 1, 1, 9, 20, tzinfo=dt.UTC)


def state(
    strike: int,
    option_type: OptionType,
    *,
    oi_pct: float = 20.0,
    prem_pct: float = 10.0,
    vol_pct: float = 30.0,
    oi: int = 20_000,
    volume: int = 5_000,
    premium: float = 100.0,
    secs: float = 5.0,
) -> StrikeState:
    """Build a StrikeState with explicit deltas (never a first observation)."""
    return StrikeState(
        strike=Decimal(strike),
        option_type=option_type,
        expiry=dt.date(2026, 1, 8),
        current_oi=oi,
        previous_oi=oi - 1,
        oi_change=1,
        oi_change_pct=oi_pct,
        current_premium=Decimal(str(premium)),
        previous_premium=Decimal(str(premium)),
        premium_change=Decimal(0),
        premium_change_pct=prem_pct,
        current_volume=volume,
        previous_volume=volume - 1,
        volume_change=1,
        volume_change_pct=vol_pct,
        last_updated=_T0,
        seconds_since_update=secs,
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


def unusual(strike: int, option_type: OptionType, triggers: int) -> UnusualActivity:
    names = ["oi_change", "volume_change", "premium_change", "oi_velocity"][:triggers]
    return UnusualActivity(
        strike=Decimal(strike),
        option_type=option_type,
        triggers=names,
        evidence=[f"{name} exceeded" for name in names],
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


def momentum(state_: MomentumState = MomentumState.INCREASING) -> MomentumReport:
    return MomentumReport(state=state_, evidence=["momentum"])


def context(
    *,
    controlling: ControllingSide = ControllingSide.BULLS,
    dominant: DominantParticipant = DominantParticipant.BUYERS,
    contradiction: str | None = None,
) -> MarketContext:
    return MarketContext(
        controlling_side=controlling,
        dominant_participant=dominant,
        momentum=MomentumState.INCREASING,
        momentum_strengthening=True,
        momentum_weakening=False,
        structure_trend=TrendDirection.UPTREND,
        structure_validates_options=True,
        contradiction=contradiction,
        immediate_support=Decimal(24650),
        immediate_resistance=Decimal(24750),
        statements=["stmt"],
        evidence=["evidence"],
    )


def rank(
    classifications: list[ClassificationResult],
    unusuals: list[UnusualActivity],
    states: list[StrikeState],
    *,
    structure_: StructureState,
    context_: MarketContext,
    momentum_: MomentumReport | None = None,
) -> CandidateRanking:
    return rec.rank_candidates(
        classifications,
        unusuals,
        states,
        structure_,
        momentum_ or momentum(),
        context_,
        min_conviction=2,
        min_oi=0,
        min_volume=0,
        max_staleness_seconds=0.0,
    )


# --- Stage 2: classification preference --------------------------------------


def test_long_buildup_beats_short_covering() -> None:
    # Two CE candidates, identical in every other respect; only the
    # classification differs. Long Build-up must rank above Short Covering.
    classifications = [
        classification(24700, OptionType.CE, Classification.SHORT_COVERING),
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
    ]
    states = [state(24700, OptionType.CE), state(24750, OptionType.CE)]
    unusuals = [unusual(24700, OptionType.CE, 2), unusual(24750, OptionType.CE, 2)]

    # Context does NOT explicitly support Short Covering (controlling side is
    # neutral), so Long Build-up must rank above it.
    ranking = rank(
        classifications,
        unusuals,
        states,
        structure_=structure(),
        context_=context(controlling=ControllingSide.NEUTRAL),
    )

    assert ranking.ranked[0].result.classification is Classification.LONG_BUILDUP
    assert ranking.best_ce is not None
    assert ranking.best_ce.result.strike == Decimal(24750)


# --- Stage 3: unusual conviction ---------------------------------------------


def test_multiple_unusual_signals_outrank_one() -> None:
    classifications = [
        classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
    ]
    states = [state(24700, OptionType.CE), state(24750, OptionType.CE)]
    unusuals = [unusual(24700, OptionType.CE, 1), unusual(24750, OptionType.CE, 3)]

    ranking = rank(
        classifications, unusuals, states, structure_=structure(), context_=context()
    )

    assert ranking.ranked[0].result.strike == Decimal(24750)  # 3 signals beats 1


# --- Stage 4: structure alignment / rejection --------------------------------


def test_structure_alignment_selects_aligned_side() -> None:
    # Uptrend/breakout market: the CE (aligned) is chosen; the PE (fighting) is
    # rejected in Stage 1 and never appears.
    classifications = [
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
        classification(24700, OptionType.PE, Classification.LONG_BUILDUP),
    ]
    states = [state(24750, OptionType.CE), state(24700, OptionType.PE)]
    unusuals = [unusual(24750, OptionType.CE, 2), unusual(24700, OptionType.PE, 2)]

    ranking = rank(
        classifications, unusuals, states, structure_=structure(), context_=context()
    )

    assert ranking.best_ce is not None
    assert ranking.best_pe is None
    assert all(c.result.option_type is OptionType.CE for c in ranking.ranked)


def test_contradicting_structure_loses() -> None:
    # A lone CE candidate that fights a downtrend/breakdown market is rejected,
    # leaving no candidates at all.
    classifications = [
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP)
    ]
    states = [state(24750, OptionType.CE)]
    unusuals = [unusual(24750, OptionType.CE, 3)]

    ranking = rank(
        classifications,
        unusuals,
        states,
        structure_=structure(
            pattern=StructurePattern.BREAKDOWN, trend=TrendDirection.DOWNTREND
        ),
        context_=context(controlling=ControllingSide.BEARS),
    )

    assert ranking.ranked == []
    assert ranking.best_ce is None


# --- Stage 6: neighbour comparison by evidence, never strike number ----------


def test_neighbour_comparison_uses_evidence_not_strike_number() -> None:
    # Two neighbouring CE candidates identical through Stages 2-5; only evidence
    # magnitude differs. The higher strike has stronger evidence, so it must win
    # — proving selection is by evidence, not the lower strike number.
    classifications = [
        classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
    ]
    states = [
        state(24700, OptionType.CE, oi_pct=10.0, prem_pct=5.0, vol_pct=10.0),
        state(24750, OptionType.CE, oi_pct=40.0, prem_pct=25.0, vol_pct=80.0),
    ]
    unusuals = [unusual(24700, OptionType.CE, 2), unusual(24750, OptionType.CE, 2)]

    ranking = rank(
        classifications, unusuals, states, structure_=structure(), context_=context()
    )

    assert ranking.ranked[0].result.strike == Decimal(24750)
    assert ranking.best_ce is not None
    assert ranking.best_ce.result.strike == Decimal(24750)


def test_indistinguishable_top_returns_no_winner() -> None:
    # Two CE candidates with byte-identical conviction keys (same everything).
    # No arbitrary strike-number pick: best_ce is None so No-Trade decides.
    classifications = [
        classification(24700, OptionType.CE, Classification.LONG_BUILDUP),
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
    ]
    states = [state(24700, OptionType.CE), state(24750, OptionType.CE)]
    unusuals = [unusual(24700, OptionType.CE, 2), unusual(24750, OptionType.CE, 2)]

    ranking = rank(
        classifications, unusuals, states, structure_=structure(), context_=context()
    )

    assert len(ranking.ranked) == 2
    assert ranking.best_ce is None  # indistinguishable → deferred to No-Trade


# --- Determinism -------------------------------------------------------------


def test_identical_input_produces_identical_output() -> None:
    def run() -> dict[str, object]:
        classifications = [
            classification(24700, OptionType.CE, Classification.SHORT_COVERING),
            classification(24750, OptionType.CE, Classification.LONG_BUILDUP),
            classification(24650, OptionType.PE, Classification.LONG_BUILDUP),
        ]
        states = [
            state(24700, OptionType.CE),
            state(24750, OptionType.CE, oi_pct=35.0),
            state(24650, OptionType.PE),
        ]
        unusuals = [unusual(24750, OptionType.CE, 3)]
        ranking = rank(
            classifications,
            unusuals,
            states,
            structure_=structure(),
            context_=context(),
        )
        report = rec.build_report(
            ranking,
            NoTradeDecision(no_trade=False, reasons=[]),
            top_n=5,
            min_conviction=2,
        )
        return report.model_dump()

    assert run() == run()


# --- Evidence is factual only ------------------------------------------------


def test_recommendation_evidence_is_factual_only() -> None:
    classifications = [
        classification(24750, OptionType.CE, Classification.LONG_BUILDUP)
    ]
    states = [state(24750, OptionType.CE)]
    unusuals = [unusual(24750, OptionType.CE, 3)]
    ranking = rank(
        classifications, unusuals, states, structure_=structure(), context_=context()
    )
    report = rec.build_report(
        ranking, NoTradeDecision(no_trade=False, reasons=[]), top_n=5, min_conviction=2
    )

    assert report.best_ce is not None
    banned = (
        "confidence",
        "confident",
        "guaranteed",
        "certain",
        "excellent",
        "amazing",
        "great",
        "sure thing",
        "%",  # no confidence percentages in engine-authored lines (see below)
    )
    engine_authored = [
        line
        for line in report.best_ce.evidence
        if line
        not in {"OI ↑ 20.0%", "Premium ↑ 10.0%", "Volume ↑ 30.0%"}  # factual deltas
    ]
    for line in engine_authored:
        lowered = line.lower()
        assert all(word not in lowered for word in banned)
    # Every evidence line is a non-empty factual string.
    assert all(isinstance(line, str) and line for line in report.best_ce.evidence)
    assert report.best_ce.reason
