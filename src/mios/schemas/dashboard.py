"""Dashboard aggregation contract.

A single response bundling everything a decision-centric dashboard needs,
assembled from one pipeline execution held in the engine store. Nested sections
reuse the existing `mios.schemas.market` schemas unchanged; this module adds the
envelope plus the presentation projections (narrative, dominance, market header,
option-chain rows, engine status).
"""

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel

from mios.config.constants import AuthStatus, ConnectionState, DataSource
from mios.schemas.market import (
    CePeComparison,
    Classification,
    ControllingSide,
    MarketContext,
    OptionType,
    TradeQualification,
)


class MarketSection(BaseModel):
    """Spot price and session status for the dashboard header."""

    spot: Decimal | None
    change: Decimal | None
    change_percent: float | None
    status: str  # "LIVE" | "CLOSED"
    updated_at: dt.datetime | None


class MarketNarrative(BaseModel):
    """A plain-language story of the market for the top-of-dashboard banner."""

    tone: str  # "bullish" | "bearish" | "neutral"
    headline: str
    #: The "what is happening now" bullet lines.
    statements: list[str]


class MarketDominance(BaseModel):
    """Who controls the market, derived from the existing CE/PE analysis."""

    control: ControllingSide
    buyers_pct: int
    writers_pct: int
    ce_dominance: str  # "Strong" | "Balanced" | "Weak"
    pe_dominance: str
    control_shift_from: str
    control_shift_to: str


class OptionChainRow(BaseModel):
    """One strike, projected from already-computed pipeline outputs."""

    strike: Decimal
    option_type: OptionType
    premium: Decimal
    oi: int
    oi_change: int
    volume: int
    classification: Classification | None
    unusual_flags: list[str]
    recommendation_flag: bool


class EngineStatus(BaseModel):
    """Operational status of the live engine."""

    healthy: bool
    pipeline_runtime_ms: float | None
    data_age_seconds: float | None


class DashboardResponse(BaseModel):
    """Everything the decision-centric dashboard needs, from one pipeline run."""

    #: Fyers connection lifecycle state — exactly one of the five values.
    connection_state: ConnectionState
    #: Fyers authentication state — CONNECTED or NOT_AUTHENTICATED.
    authentication: AuthStatus
    #: Which source is feeding the engine (fyers / simulator / none).
    data_source: DataSource
    market: MarketSection
    narrative: MarketNarrative | None
    dominance: MarketDominance | None
    qualification: TradeQualification | None
    context: MarketContext | None
    ce_pe: CePeComparison | None
    #: Trimmed to the five CE and five PE strikes nearest the money.
    option_chain: list[OptionChainRow]
    engine: EngineStatus
