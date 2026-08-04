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
    MarketBias,
    MarketContext,
    MomentumState,
    OptionType,
    Sentiment,
    StructurePattern,
    TradeQualification,
    TrendDirection,
)


class MarketSection(BaseModel):
    """Spot price and session status for the dashboard header."""

    spot: Decimal | None
    #: The at-the-money strike: the strike nearest spot on the existing strike
    #: ladder (`round(spot / step) * step`). Pure display math over values the
    #: pipeline already holds (spot, strike step) — it anchors the Participation
    #: Radar's ATM±2 window and touches no analysis, classification, or
    #: qualification logic.
    atm_strike: Decimal | None
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


class ParticipationRow(BaseModel):
    """One strike in the Participation Radar, ranked by fresh OI positioning.

    Ranking and every value come from existing engine outputs (the Radar
    engine's OI-addition ordering plus the Option Engine's already-computed
    percentage changes and classification) — nothing new is calculated here.
    """

    rank: int
    strike: Decimal
    option_type: OptionType
    classification: Classification | None
    oi_change: int
    oi_change_pct: float | None
    premium_change_pct: float | None
    volume_change_pct: float | None


class StrikeHistoryPoint(BaseModel):
    """One persisted snapshot of a strike, for the Strike Evolution panel."""

    captured_at: dt.datetime
    oi: int
    oi_change: int
    oi_change_pct: float | None
    premium: Decimal
    premium_change: Decimal
    premium_change_pct: float | None
    volume: int
    volume_change: int
    volume_change_pct: float | None
    classification: Classification | None


class StrikeHistory(BaseModel):
    """The historical progression of one strike, oldest first."""

    strike: Decimal
    option_type: OptionType
    points: list[StrikeHistoryPoint]


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
    #: Strikes with the strongest fresh participation, ranked (Radar engine).
    participation: list[ParticipationRow]
    context: MarketContext | None
    ce_pe: CePeComparison | None
    #: Trimmed to the five CE and five PE strikes nearest the money.
    option_chain: list[OptionChainRow]
    engine: EngineStatus


# --- Debug / audit ------------------------------------------------------------


class AuditStrikeRow(BaseModel):
    """One nearby strike in the decision trace, with its bias contribution."""

    strike: Decimal
    option_type: OptionType
    oi_change: int
    oi_change_pct: float | None
    premium_change_pct: float | None
    volume_change_pct: float | None
    classification: Classification | None
    sentiment: Sentiment | None
    weight: int
    signed_score: float


class AuditReport(BaseModel):
    """A full, explainable decision trace for one market snapshot.

    The primary MIOS debugging tool: every dashboard conclusion (bias, regime,
    dominance, qualification, narrative) shown next to the raw per-strike
    evidence it was derived from, plus any consistency contradictions found.
    """

    spot: Decimal | None
    atm: Decimal | None
    strikes: list[AuditStrikeRow]
    bias: MarketBias | None
    structure_trend: TrendDirection | None
    structure_pattern: StructurePattern | None
    momentum: MomentumState | None
    dominance: MarketDominance | None
    qualification: TradeQualification | None
    narrative: MarketNarrative | None
    consistency_warnings: list[str]
