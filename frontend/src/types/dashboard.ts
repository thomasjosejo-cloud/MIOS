// Types mirroring the backend `GET /api/v1/dashboard` contract
// (mios.schemas.dashboard). The backend serializes Decimal fields as JSON
// strings and int fields as numbers, so those are typed accordingly here.

export type OptionType = "CE" | "PE";

export type Classification =
  | "long_buildup"
  | "short_buildup"
  | "long_unwinding"
  | "short_covering";

export type ControllingSide = "bulls" | "bears" | "neutral";
export type TrendDirection = "uptrend" | "downtrend" | "sideways";
export type MomentumState = "increasing" | "decreasing" | "neutral";
export type DominantParticipant = "buyers" | "writers" | "balanced";
export type MarketSide = "CE" | "PE" | "neutral";

export interface MarketSection {
  spot: string | null;
  change: string | null;
  change_percent: number | null;
  status: "LIVE" | "CLOSED";
  updated_at: string | null;
}

export interface StrikeRecommendation {
  strike: string;
  option_type: OptionType;
  classification: Classification;
  evidence: string[];
  reason: string;
}

export interface NoTradeDecision {
  no_trade: boolean;
  reasons: string[];
}

export interface RecommendationReport {
  best_ce: StrikeRecommendation | null;
  best_pe: StrikeRecommendation | null;
  top_candidates: StrikeRecommendation[];
  no_trade: NoTradeDecision;
}

export interface MarketContext {
  controlling_side: ControllingSide;
  dominant_participant: DominantParticipant;
  momentum: MomentumState;
  momentum_strengthening: boolean;
  momentum_weakening: boolean;
  structure_trend: TrendDirection;
  structure_validates_options: boolean;
  contradiction: string | null;
  immediate_support: string | null;
  immediate_resistance: string | null;
  statements: string[];
  evidence: string[];
}

export interface CePeComparison {
  stronger_side: MarketSide;
  writer_active_strikes: string[];
  buyer_active_strikes: string[];
  control_shifting: boolean;
  shift_description: string | null;
  important_strikes: string[];
  evidence: string[];
}

export interface OptionChainRow {
  strike: string;
  option_type: OptionType;
  premium: string;
  oi: number;
  oi_change: number;
  volume: number;
  classification: Classification | null;
  unusual_flags: string[];
  recommendation_flag: boolean;
}

export interface EngineStatus {
  healthy: boolean;
  pipeline_runtime_ms: number | null;
  data_age_seconds: number | null;
}

export interface DashboardResponse {
  market: MarketSection;
  recommendation: RecommendationReport | null;
  no_trade: NoTradeDecision | null;
  context: MarketContext | null;
  ce_pe: CePeComparison | null;
  top_candidates: StrikeRecommendation[];
  option_chain: OptionChainRow[];
  engine: EngineStatus;
}
