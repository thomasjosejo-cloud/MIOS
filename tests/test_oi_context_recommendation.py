"""Tests for the Context, Recommendation, and No-Trade engines."""

from collections.abc import Callable
from decimal import Decimal

from mios.schemas.market import (
    Candle,
    ClassificationResult,
    ControllingSide,
    MarketContext,
    MomentumReport,
    OptionQuote,
    OptionType,
    RecommendationReport,
    StrikeState,
    StructureState,
    TrendDirection,
    UnusualActivity,
)
from mios.services.options_intel import (
    ce_pe,
    unusual_activity,
)
from mios.services.options_intel import (
    context as context_engine,
)
from mios.services.options_intel import (
    momentum as momentum_engine,
)
from mios.services.options_intel import (
    no_trade as no_trade_engine,
)
from mios.services.options_intel import (
    recommendation as recommendation_engine,
)
from mios.services.options_intel import (
    structure as structure_engine,
)
from mios.services.options_intel.classification import classify_all
from mios.services.options_intel.option_engine import OptionEngine

QuoteFactory = Callable[..., OptionQuote]
CandleFactory = Callable[[list[float]], list[Candle]]


def _recommend(
    classifications: list[ClassificationResult],
    unusual: list[UnusualActivity],
    strike_states: list[StrikeState],
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
    *,
    top_n: int,
    min_evidence: int,
    rank_tie_margin: int,
    min_no_trade_reasons: int,
) -> RecommendationReport:
    """Drive the pipeline's rank -> no-trade -> build-report sequence.

    Mirrors `pipeline.run_pipeline` so the tests exercise the same orchestration
    the Pipeline performs now that Recommendation no longer calls No-Trade.
    Stage-1 liquidity/staleness gates are left permissive (0) here.
    """
    ranking = recommendation_engine.rank_candidates(
        classifications,
        unusual,
        strike_states,
        structure,
        momentum,
        context,
        min_conviction=min_evidence,
        min_oi=0,
        min_volume=0,
        max_staleness_seconds=0.0,
    )
    no_trade = no_trade_engine.evaluate(
        context,
        structure,
        momentum,
        ce_rank=ranking.best_ce_score,
        pe_rank=ranking.best_pe_score,
        rank_tie_margin=rank_tie_margin,
        min_reasons=min_no_trade_reasons,
    )
    return recommendation_engine.build_report(
        ranking, no_trade, top_n=top_n, min_conviction=min_evidence
    )


def _bullish_states(make: QuoteFactory) -> list[StrikeState]:
    """Put writing at 24600 (support) and call buying at 24800 (above spot 24750)."""
    engine = OptionEngine()
    strikes = [24600, 24700, 24750, 24800]
    for strike in strikes:
        for option_type in (OptionType.CE, OptionType.PE):
            engine.update(
                make(
                    strike=strike,
                    option_type=option_type,
                    oi=10_000,
                    premium=100,
                    volume=1000,
                )
            )

    changes = {
        (24600, OptionType.PE): {"oi": 18_000, "premium": 80, "volume": 6000},
        (24800, OptionType.CE): {"oi": 17_000, "premium": 140, "volume": 7000},
    }
    states = []
    for strike in strikes:
        for option_type in (OptionType.CE, OptionType.PE):
            c = changes.get(
                (strike, option_type), {"oi": 10_050, "premium": 100.5, "volume": 1010}
            )
            states.append(
                engine.update(
                    make(
                        strike=strike,
                        option_type=option_type,
                        oi=c["oi"],
                        premium=c["premium"],
                        volume=c["volume"],
                        minutes=5,
                    )
                )
            )
    return states


def test_context_is_evidence_backed_and_names_control(
    make_option_quote: QuoteFactory,
    make_candles: CandleFactory,
    zigzag_uptrend_closes: list[float],
) -> None:
    states = _bullish_states(make_option_quote)
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    unusual = unusual_activity.detect(
        states,
        oi_change_pct=40,
        volume_change_pct=100,
        premium_change_pct=20,
        oi_velocity_per_min=500,
    )
    cepe = ce_pe.compare(
        states, classifications, unusual, neutral_band_pct=10, previous=None
    )
    candles = make_candles(zigzag_uptrend_closes)
    structure = structure_engine.analyze(candles, swing_lookback=2)
    momentum = momentum_engine.analyze(
        candles, structure, lookback=5, acceleration_threshold=0.2
    )

    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24750)
    )

    assert context.controlling_side is ControllingSide.BULLS
    assert context.evidence  # never empty
    assert any("Put Writing" in s for s in context.statements)
    assert any("Call Buying" in s for s in context.statements)


def test_context_flags_contradiction(
    make_option_quote: QuoteFactory, make_candles: CandleFactory
) -> None:
    # Bullish options activity but a downtrend in price structure.
    states = _bullish_states(make_option_quote)
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    cepe = ce_pe.compare(
        states, classifications, [], neutral_band_pct=10, previous=None
    )

    down_closes: list[int] = []
    points = [24800, 24700, 24760, 24620, 24680, 24540]
    for i in range(len(points) - 1):
        s, e = points[i], points[i + 1]
        down_closes.extend(range(s, e, 1 if e > s else -1))
    down_closes.append(points[-1])
    candles = make_candles([float(c) for c in down_closes])
    structure = structure_engine.analyze(candles, swing_lookback=2)
    momentum = momentum_engine.analyze(
        candles, structure, lookback=5, acceleration_threshold=0.2
    )

    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24750)
    )

    if (
        structure.trend is TrendDirection.DOWNTREND
        and context.controlling_side is ControllingSide.BULLS
    ):
        assert context.contradiction is not None


def test_recommendation_prefers_supported_ce(
    make_option_quote: QuoteFactory,
    make_candles: CandleFactory,
    zigzag_uptrend_closes: list[float],
) -> None:
    states = _bullish_states(make_option_quote)
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    unusual = unusual_activity.detect(
        states,
        oi_change_pct=40,
        volume_change_pct=100,
        premium_change_pct=20,
        oi_velocity_per_min=500,
    )
    cepe = ce_pe.compare(
        states, classifications, unusual, neutral_band_pct=10, previous=None
    )
    candles = make_candles(zigzag_uptrend_closes)
    structure = structure_engine.analyze(candles, swing_lookback=2)
    momentum = momentum_engine.analyze(
        candles, structure, lookback=5, acceleration_threshold=0.2
    )
    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24750)
    )

    report = _recommend(
        classifications,
        unusual,
        states,
        structure,
        momentum,
        context,
        top_n=5,
        min_evidence=2,
        rank_tie_margin=1,
        min_no_trade_reasons=2,
    )

    assert report.best_ce is not None
    assert report.best_ce.evidence
    assert report.best_ce.reason
    assert not report.no_trade.no_trade


def test_no_trade_when_conditions_are_weak(
    make_option_quote: QuoteFactory, make_candles: CandleFactory
) -> None:
    # Flat option chain (no classifications) and a ranging, trendless price series.
    engine = OptionEngine()
    for strike in (24700, 24750):
        for ot in (OptionType.CE, OptionType.PE):
            engine.update(
                make_option_quote(strike=strike, option_type=ot, oi=10_000, premium=100)
            )
    states = [
        engine.update(
            make_option_quote(
                strike=strike, option_type=ot, oi=10_010, premium=100.1, minutes=5
            )
        )
        for strike in (24700, 24750)
        for ot in (OptionType.CE, OptionType.PE)
    ]
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    cepe = ce_pe.compare(
        states, classifications, [], neutral_band_pct=10, previous=None
    )

    ranging = make_candles([24700 + (i % 3) - 1 for i in range(20)])
    structure = structure_engine.analyze(ranging, swing_lookback=2)
    momentum = momentum_engine.analyze(
        ranging, structure, lookback=5, acceleration_threshold=0.2
    )
    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24725)
    )

    report = _recommend(
        classifications,
        unusual_activity.detect(
            states,
            oi_change_pct=40,
            volume_change_pct=100,
            premium_change_pct=20,
            oi_velocity_per_min=500,
        ),
        states,
        structure,
        momentum,
        context,
        top_n=5,
        min_evidence=2,
        rank_tie_margin=1,
        min_no_trade_reasons=2,
    )

    assert report.no_trade.no_trade
    assert len(report.no_trade.reasons) >= 2
    assert all(isinstance(reason, str) and reason for reason in report.no_trade.reasons)


def test_no_trade_reasons_are_specific_not_generic(
    make_option_quote: QuoteFactory, make_candles: CandleFactory
) -> None:
    engine = OptionEngine()
    for ot in (OptionType.CE, OptionType.PE):
        engine.update(make_option_quote(strike=24700, option_type=ot))
    states = [
        engine.update(make_option_quote(strike=24700, option_type=ot, minutes=5))
        for ot in (OptionType.CE, OptionType.PE)
    ]
    ranging = make_candles([24700 + (i % 3) - 1 for i in range(20)])
    structure = structure_engine.analyze(ranging, swing_lookback=2)
    momentum = momentum_engine.analyze(
        ranging, structure, lookback=5, acceleration_threshold=0.2
    )
    cepe = ce_pe.compare(states, [], [], neutral_band_pct=10, previous=None)
    context = context_engine.build_context(
        cepe, structure, momentum, [], spot=Decimal(24700)
    )

    report = _recommend(
        [],
        [],
        states,
        structure,
        momentum,
        context,
        top_n=5,
        min_evidence=2,
        rank_tie_margin=1,
        min_no_trade_reasons=2,
    )

    joined = " ".join(report.no_trade.reasons).lower()
    assert any(
        term in joined
        for term in ("structure", "momentum", "range", "candidate", "dominant")
    )
