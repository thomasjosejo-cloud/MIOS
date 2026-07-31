"""In-memory latest-state store for the live engine.

Holds the most recent output of each engine so the `/market/*` endpoints can
serve the current view without recomputing or touching the database. A single
instance is created at startup and shared; the polling loop is the only writer.
"""

import datetime as dt
from dataclasses import dataclass, field
from decimal import Decimal

from mios.config.constants import ConnectionState, DataSource
from mios.schemas.market import (
    CePeComparison,
    ClassificationResult,
    ControllingSide,
    MarketBias,
    MarketContext,
    MomentumReport,
    RadarReport,
    StrikeState,
    StructureState,
    TradeQualification,
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
    bias: MarketBias | None = None
    structure: StructureState | None = None
    momentum: MomentumReport | None = None
    context: MarketContext | None = None
    qualification: TradeQualification | None = None

    spot_price: Decimal | None = None
    #: Previous trading day's close (from the feed) — the baseline for the
    #: day's change. Never the previous poll's price.
    spot_prev_close: Decimal | None = None
    #: Canonical control from the previous poll, for the dominance shift arrow.
    previous_controlling_side: ControllingSide | None = None
    market_open: bool = False
    engine_running: bool = False
    #: Whether the optional 5-minute History validation step ran this poll.
    #: False marks validation as "Unavailable" (History endpoint failed);
    #: option-chain intelligence still produced context and recommendations.
    validation_available: bool = True
    #: Whether a validated Fyers session currently drives the engine.
    authenticated: bool = False
    #: Which source is feeding the engine (fyers / simulator / none).
    data_source: DataSource = DataSource.NONE
    #: The Fyers connection lifecycle state shown on the dashboard.
    connection_state: ConnectionState = ConnectionState.NOT_CONNECTED
    last_poll_at: dt.datetime | None = None
    #: Wall-clock duration of the most recent pipeline run, in milliseconds.
    last_pipeline_runtime_ms: float | None = None
    last_error: str | None = None
