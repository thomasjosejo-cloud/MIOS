"""Dashboard aggregation contract.

A single response bundling everything a live dashboard needs, assembled from
the outputs of one pipeline execution already held in the engine store. Nested
sections reuse the existing `mios.schemas.market` schemas unchanged; this module
only adds the envelope and the dashboard-specific market/option-chain/engine
projections.
"""

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel

from mios.config.constants import AuthStatus, DataSource
from mios.schemas.market import (
    CePeComparison,
    Classification,
    MarketContext,
    NoTradeDecision,
    OptionType,
    RecommendationReport,
    StrikeRecommendation,
)


class MarketSection(BaseModel):
    """Spot price and session status for the dashboard header."""

    spot: Decimal | None
    change: Decimal | None
    change_percent: float | None
    status: str  # "LIVE" | "CLOSED"
    updated_at: dt.datetime | None


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
    """Everything the dashboard needs, from one pipeline execution."""

    #: Fyers authentication state — CONNECTED or NOT_AUTHENTICATED.
    authentication: AuthStatus
    #: Which source is feeding the engine (fyers / simulator / none).
    data_source: DataSource
    market: MarketSection
    recommendation: RecommendationReport | None
    no_trade: NoTradeDecision | None
    context: MarketContext | None
    ce_pe: CePeComparison | None
    top_candidates: list[StrikeRecommendation]
    option_chain: list[OptionChainRow]
    engine: EngineStatus
