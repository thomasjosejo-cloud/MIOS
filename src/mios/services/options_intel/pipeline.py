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
    MarketBias,
    MarketContext,
    MomentumReport,
    OptionQuote,
    RadarReport,
    StrikeState,
    StructureState,
    TradeQualification,
    UnusualActivity,
)
from mios.services.options_intel import (
    bias as bias_engine,
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
    qualification as qualification_engine,
)
from mios.services.options_intel import (
    radar as radar_engine,
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
    bias: MarketBias
    structure: StructureState
    momentum: MomentumReport
    context: MarketContext
    qualification: TradeQualification


def run_pipeline(
    *,
    option_engine: OptionEngine,
    option_quotes: list[OptionQuote],
    candles: list[Candle],
    spot: Decimal,
    settings: Settings,
    previous_cepe: CePeComparison | None,
    session_open: Decimal | None = None,
    prev_close: Decimal | None = None,
) -> PipelineResult:
    """Run every engine in order for one poll and return all outputs.

    `session_open` and `prev_close` are session-scoped state owned by the
    orchestrator, passed through to the Context Engine solely so it can describe
    the opening gap; no engine here computes or retains them.
    """
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
    # The canonical read of market control. Every component below derives who
    # is in control from this one object, so they cannot contradict each other.
    bias = bias_engine.assess(
        classifications,
        strike_states,
        neutral_band_pct=settings.CE_PE_NEUTRAL_BAND_PCT,
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
        cepe,
        structure,
        momentum,
        classifications,
        bias,
        spot=spot,
        session_open=session_open,
        prev_close=prev_close,
    )
    # The Trade Qualification Engine makes the final decision from the four
    # gates, reading the upstream outputs only.
    qualification = qualification_engine.qualify(
        classifications,
        unusual,
        strike_states,
        structure,
        context,
        bias,
        spot=spot,
        settings=settings,
    )

    return PipelineResult(
        strike_states=strike_states,
        classifications=classifications,
        unusual=unusual,
        radar=radar,
        cepe=cepe,
        bias=bias,
        structure=structure,
        momentum=momentum,
        context=context,
        qualification=qualification,
    )
