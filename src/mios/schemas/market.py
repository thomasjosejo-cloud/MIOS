"""Options intelligence domain contracts.

These schemas are shared end-to-end: the same shapes produced internally by the
engines in `mios.services.options_intel` are what the `/market/*` endpoints
return. There is deliberately no confidence score or percentage anywhere in
this module — every output is either a fact (a price, a count, a change) or an
evidence-backed classification, per the product requirement that this system
explains itself rather than scoring itself.
"""

import datetime as dt
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class OptionType(StrEnum):
    """Side of an option contract."""

    CE = "CE"
    PE = "PE"


class Classification(StrEnum):
    """The four canonical options positioning behaviours."""

    LONG_BUILDUP = "long_buildup"
    SHORT_BUILDUP = "short_buildup"
    LONG_UNWINDING = "long_unwinding"
    SHORT_COVERING = "short_covering"


class Sentiment(StrEnum):
    """The directional market meaning of a classified strike.

    A position label (e.g. Short Build-up) means the opposite thing on the CE
    and PE side: writing calls is bearish, writing puts is bullish. This enum is
    that resolved meaning, produced by the Bias Engine's canonical mapping.
    """

    BULLISH = "bullish"
    BEARISH = "bearish"


class SwingLabel(StrEnum):
    """Label applied to a detected swing point relative to the prior one."""

    HH = "HH"
    HL = "HL"
    LH = "LH"
    LL = "LL"


class TrendDirection(StrEnum):
    """Direction implied by the most recent swing sequence."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"


class StructurePattern(StrEnum):
    """Current price action pattern relative to recent structure."""

    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"
    PULLBACK = "pullback"
    RANGE = "range"


class MomentumState(StrEnum):
    """Whether the rate of movement is accelerating, fading, or steady."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    NEUTRAL = "neutral"


class MarketSide(StrEnum):
    """Which side of the options market is stronger, if either."""

    CE = "CE"
    PE = "PE"
    NEUTRAL = "neutral"


class DominantParticipant(StrEnum):
    """Whether option buyers or option writers are driving the activity."""

    BUYERS = "buyers"
    WRITERS = "writers"
    BALANCED = "balanced"


class ControllingSide(StrEnum):
    """Which directional bias currently controls the market."""

    BULLS = "bulls"
    BEARS = "bears"
    NEUTRAL = "neutral"


# --- Normalized market data ---------------------------------------------------


class SpotQuote(BaseModel):
    """Normalized spot price observation.

    `prev_close` is the previous trading day's close, straight from the feed —
    the correct baseline for the day's change (never the previous poll's price).
    `change` and `change_percent` are derived from it so every consumer reports
    the same daily change the exchange does.
    """

    symbol: str
    ltp: Decimal
    prev_close: Decimal | None = None
    timestamp: dt.datetime

    @property
    def change(self) -> Decimal | None:
        """Absolute change from the previous close, or None if unavailable."""
        if self.prev_close is None:
            return None
        return self.ltp - self.prev_close

    @property
    def change_percent(self) -> float | None:
        """Percent change from the previous close, or None if unavailable."""
        if self.prev_close is None or self.prev_close == 0:
            return None
        return round(float((self.ltp - self.prev_close) / self.prev_close * 100), 2)


class OptionQuote(BaseModel):
    """Normalized single-strike option observation."""

    symbol: str
    strike: Decimal
    option_type: OptionType
    expiry: dt.date
    premium: Decimal
    oi: int = Field(ge=0)
    volume: int = Field(ge=0)
    timestamp: dt.datetime


class Candle(BaseModel):
    """A single OHLCV candle."""

    symbol: str
    timestamp: dt.datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = Field(ge=0)


# --- Option Engine --------------------------------------------------------------


class StrikeState(BaseModel):
    """Latest tracked state for one strike, with deltas from the prior poll."""

    strike: Decimal
    option_type: OptionType
    expiry: dt.date

    current_oi: int
    previous_oi: int | None = None
    oi_change: int = 0
    oi_change_pct: float | None = None
    oi_velocity_per_min: float | None = None

    current_premium: Decimal
    previous_premium: Decimal | None = None
    premium_change: Decimal = Decimal(0)
    premium_change_pct: float | None = None

    current_volume: int
    previous_volume: int | None = None
    volume_change: int = 0
    volume_change_pct: float | None = None

    last_updated: dt.datetime
    seconds_since_update: float = 0.0

    @property
    def is_first_observation(self) -> bool:
        """Whether this strike has no prior state to compare against."""
        return self.previous_oi is None


# --- Classification Engine -------------------------------------------------------


class ClassificationResult(BaseModel):
    """An evidence-backed classification for a single strike."""

    strike: Decimal
    option_type: OptionType
    classification: Classification
    evidence: list[str]
    reason: str


# --- Unusual Activity Engine ------------------------------------------------------


class UnusualActivity(BaseModel):
    """A strike whose activity crossed a configured threshold."""

    strike: Decimal
    option_type: OptionType
    triggers: list[str]
    evidence: list[str]


# --- Options Radar -----------------------------------------------------------------


class StrikeActivity(BaseModel):
    """A single ranked entry in a radar list."""

    strike: Decimal
    option_type: OptionType
    metric: str
    value: Decimal


class RadarReport(BaseModel):
    """The seven ranked activity views across the option chain."""

    top_ce_activity: list[StrikeActivity]
    top_pe_activity: list[StrikeActivity]
    highest_oi_addition: list[StrikeActivity]
    highest_oi_reduction: list[StrikeActivity]
    highest_volume: list[StrikeActivity]
    highest_premium_expansion: list[StrikeActivity]
    highest_oi_velocity: list[StrikeActivity]


# --- CE vs PE Engine ----------------------------------------------------------------


class CePeComparison(BaseModel):
    """Comparison of Call and Put side activity."""

    stronger_side: MarketSide
    writer_active_strikes: list[Decimal]
    buyer_active_strikes: list[Decimal]
    control_shifting: bool
    shift_description: str | None
    important_strikes: list[Decimal]
    evidence: list[str]


# --- Structure Engine ---------------------------------------------------------------


class SwingPoint(BaseModel):
    """A detected swing high or low."""

    timestamp: dt.datetime
    price: Decimal
    label: SwingLabel


class StructureState(BaseModel):
    """Price structure derived from recent candles."""

    swing_high: Decimal | None
    swing_low: Decimal | None
    immediate_support: Decimal | None
    immediate_resistance: Decimal | None
    pattern: StructurePattern
    trend: TrendDirection
    swings: list[SwingPoint] = Field(default_factory=list)
    evidence: list[str]


# --- Momentum Engine -----------------------------------------------------------------


class MomentumReport(BaseModel):
    """Momentum state derived from price and volume behaviour."""

    state: MomentumState
    evidence: list[str]


# --- Bias Engine (canonical market control) ------------------------------------------


class StrikeContribution(BaseModel):
    """One classified strike's signed contribution to the market bias.

    `weight` is the magnitude of fresh positioning (|OI change|); `signed_score`
    is that weight with the sentiment's sign. Nothing here is invented — the
    weight is already-computed OI data and the sentiment is a fixed mapping.
    """

    strike: Decimal
    option_type: OptionType
    classification: Classification
    sentiment: Sentiment
    weight: int
    signed_score: float


class MarketBias(BaseModel):
    """The single canonical read of who controls the market.

    Every downstream component (context, dominance, qualification, narrative)
    derives market control from this one object, so they can never disagree.
    Control is decided from classification-resolved sentiment weighted by OI
    change — never from raw OI direction alone.
    """

    controlling_side: ControllingSide
    bull_score: float
    bear_score: float
    net_score: float
    contributions: list[StrikeContribution]
    evidence: list[str]


# --- Context Engine ------------------------------------------------------------------


class MarketContext(BaseModel):
    """Synthesized, evidence-backed explanation of the current market state."""

    controlling_side: ControllingSide
    dominant_participant: DominantParticipant
    momentum: MomentumState
    momentum_strengthening: bool
    momentum_weakening: bool
    structure_trend: TrendDirection
    structure_validates_options: bool
    contradiction: str | None
    immediate_support: Decimal | None
    immediate_resistance: Decimal | None
    statements: list[str]
    evidence: list[str]


# --- Trade Qualification Engine -------------------------------------------------------


class TradeDecision(StrEnum):
    """The qualification engine's final decision."""

    BUY_CE = "BUY_CE"
    BUY_PE = "BUY_PE"
    NO_TRADE = "NO_TRADE"


class ConfidenceBand(StrEnum):
    """Human-readable band for the weighted confidence score."""

    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class GateName(StrEnum):
    """The four qualification gates, in evaluation order."""

    MARKET_REGIME = "Market Regime"
    OPTIONS_PARTICIPATION = "Options Participation"
    CE_PE_CONTROL = "CE vs PE Control"
    STRIKE_QUALITY = "Strike Quality"


class QualificationGate(BaseModel):
    """The result of one qualification gate."""

    name: GateName
    passed: bool
    reason: str
    weight: int
    mandatory: bool


class BestCandidate(BaseModel):
    """The strongest strike MIOS is watching, shown even during NO TRADE."""

    strike: Decimal
    option_type: OptionType
    classification: Classification
    qualification: int
    reason: str


class TradeQualification(BaseModel):
    """The engine's final, gate-based decision for the current poll.

    Every trade either passes qualification or does not: the four gates and the
    confidence make the decision fully explainable. A failing mandatory gate
    yields NO_TRADE, so the system is willing to stand aside indefinitely.
    `best_candidate` is always populated (when any candidate exists) so the
    trader can see what MIOS is watching even when no trade is qualified.
    """

    decision: TradeDecision
    qualified: bool
    strike: Decimal | None
    option_type: OptionType | None
    classification: Classification | None
    confidence: int
    band: ConfidenceBand
    gates: list[QualificationGate]
    failed_gates: list[GateName]
    reasons: list[str]
    best_candidate: BestCandidate | None


# --- Composite API responses ---------------------------------------------------------


class OptionsReport(BaseModel):
    """The full options-positioning view for the `/market/options` endpoint."""

    spot_price: Decimal | None
    strikes: list[StrikeState]
    classifications: list[ClassificationResult]
    unusual_activity: list[UnusualActivity]
    ce_pe: CePeComparison


class StructureReport(BaseModel):
    """Combined price structure and momentum for the `/market/structure` endpoint."""

    structure: StructureState
    momentum: MomentumReport


# --- Market status -------------------------------------------------------------------


class MarketStatusReport(BaseModel):
    """Operational status of the live engine and the underlying market."""

    market_open: bool
    session: str
    spot_price: Decimal | None
    engine_running: bool
    last_poll_at: dt.datetime | None
    last_error: str | None
