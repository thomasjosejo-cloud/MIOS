"""In-memory latest-state store for the live engine.

Holds the most recent output of each engine so the `/market/*` endpoints can
serve the current view without recomputing or touching the database. A single
instance is created at startup and shared; the polling loop is the only writer.
"""

import datetime as dt
from dataclasses import dataclass, field
from decimal import Decimal

from mios.schemas.market import (
    CePeComparison,
    ClassificationResult,
    MarketContext,
    MomentumReport,
    RadarReport,
    RecommendationReport,
    StrikeState,
    StructureState,
    UnusualActivity,
)


@dataclass
class EngineStore:
    """Latest engine outputs and run metadata, updated in place each poll."""

    strike_states: list[StrikeState] = field(default_factory=list)
    classifications: list[ClassificationResult] = field(default_factory=list)
    unusual: list[UnusualActivity] = field(default_factory=list)
    radar: RadarReport | None = None
    cepe: CePeComparison | None = None
    structure: StructureState | None = None
    momentum: MomentumReport | None = None
    context: MarketContext | None = None
    recommendation: RecommendationReport | None = None

    spot_price: Decimal | None = None
    market_open: bool = False
    engine_running: bool = False
    last_poll_at: dt.datetime | None = None
    last_error: str | None = None
