"""One pass of the analysis pipeline.

Pure with respect to I/O: given already-fetched market data, the stateful
`OptionEngine`, and the previous CE/PE comparison, it runs every engine in
order and returns the full result bundle. The orchestrator (`engine.py`) owns
fetching, persistence, and the loop; this owns the computation.
"""

from dataclasses import dataclass
from decimal import Decimal

from mios.config import Settings
from mios.schemas.market import (
    Candle,
    CePeComparison,
    ClassificationResult,
    MarketContext,
    MomentumReport,
    OptionQuote,
    RadarReport,
    RecommendationReport,
    StrikeState,
    StructureState,
    UnusualActivity,
)
from mios.services.options_intel import (
    ce_pe,
    classification,
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
    radar as radar_engine,
)
from mios.services.options_intel import (
    recommendation as recommendation_engine,
)
from mios.services.options_intel import (
    structure as structure_engine,
)
from mios.services.options_intel.option_engine import OptionEngine


@dataclass
class PipelineResult:
    """The full set of engine outputs from a single poll."""

    strike_states: list[StrikeState]
    classifications: list[ClassificationResult]
    unusual: list[UnusualActivity]
    radar: RadarReport
    cepe: CePeComparison
    structure: StructureState
    momentum: MomentumReport
    context: MarketContext
    recommendation: RecommendationReport


def run_pipeline(
    *,
    option_engine: OptionEngine,
    option_quotes: list[OptionQuote],
    candles: list[Candle],
    spot: Decimal,
    settings: Settings,
    previous_cepe: CePeComparison | None,
) -> PipelineResult:
    """Run every engine in order for one poll and return all outputs."""
    strike_states = option_engine.update_all(option_quotes)

    classifications = classification.classify_all(
        strike_states,
        min_oi_change_pct=settings.CLASSIFICATION_MIN_OI_CHANGE_PCT,
        min_premium_change_pct=settings.CLASSIFICATION_MIN_PREMIUM_CHANGE_PCT,
    )
    unusual = unusual_activity.detect(
        strike_states,
        oi_change_pct=settings.UNUSUAL_OI_CHANGE_PCT,
        volume_change_pct=settings.UNUSUAL_VOLUME_CHANGE_PCT,
        premium_change_pct=settings.UNUSUAL_PREMIUM_CHANGE_PCT,
        oi_velocity_per_min=settings.UNUSUAL_OI_VELOCITY_PER_MIN,
    )
    radar = radar_engine.build_radar(strike_states, top_n=settings.RADAR_TOP_N)
    cepe = ce_pe.compare(
        strike_states,
        classifications,
        unusual,
        neutral_band_pct=settings.CE_PE_NEUTRAL_BAND_PCT,
        previous=previous_cepe,
    )
    structure = structure_engine.analyze(
        candles, swing_lookback=settings.STRUCTURE_SWING_LOOKBACK
    )
    momentum = momentum_engine.analyze(
        candles,
        structure,
        lookback=settings.MOMENTUM_LOOKBACK_CANDLES,
        acceleration_threshold=settings.MOMENTUM_ACCELERATION_THRESHOLD,
    )
    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=spot
    )
    # Rank first so the No-Trade Engine can see the best CE/PE scores, then run
    # No-Trade, then assemble the report from both. The Pipeline is the only
    # orchestrator: Recommendation and No-Trade never call each other.
    ranking = recommendation_engine.rank_candidates(
        classifications,
        unusual,
        structure,
        momentum,
        context,
        min_evidence=settings.RECOMMENDATION_MIN_EVIDENCE,
    )
    no_trade = no_trade_engine.evaluate(
        context,
        structure,
        momentum,
        ce_rank=ranking.best_ce_score,
        pe_rank=ranking.best_pe_score,
        rank_tie_margin=settings.NO_TRADE_RANK_TIE_MARGIN,
        min_reasons=settings.NO_TRADE_MIN_REASONS,
    )
    recommendation = recommendation_engine.build_report(
        ranking,
        no_trade,
        structure,
        momentum,
        top_n=settings.RECOMMENDATION_TOP_N,
        min_evidence=settings.RECOMMENDATION_MIN_EVIDENCE,
    )

    return PipelineResult(
        strike_states=strike_states,
        classifications=classifications,
        unusual=unusual,
        radar=radar,
        cepe=cepe,
        structure=structure,
        momentum=momentum,
        context=context,
        recommendation=recommendation,
    )
