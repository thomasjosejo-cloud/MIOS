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
  // At-the-money strike (nearest strike to spot on the ladder). Anchors the
  // Participation Radar's ATM±2 window. Serialized as a decimal string.
  atm_strike: string | null;
  // The strike ladder's step (OPTION_STRIKE_STEP), used to place the ATM±k
  // rows exactly. Serialized as a number.
  strike_step: number;
  change: string | null;
  change_percent: number | null;
  status: "LIVE" | "CLOSED";
  updated_at: string | null;
}

export type TradeDecision = "BUY_CE" | "BUY_PE" | "NO_TRADE";

export type ConfidenceBand =
  | "Very Low"
  | "Low"
  | "Medium"
  | "High"
  | "Very High";

export type GateName =
  | "Market Regime"
  | "Options Participation"
  | "CE vs PE Control"
  | "Strike Quality";

export interface QualificationGate {
  name: GateName;
  passed: boolean;
  reason: string;
  weight: number;
  mandatory: boolean;
}

export interface BestCandidate {
  strike: string;
  option_type: OptionType;
  classification: Classification;
  qualification: number;
  reason: string;
}

export interface TradeQualification {
  decision: TradeDecision;
  qualified: boolean;
  strike: string | null;
  option_type: OptionType | null;
  classification: Classification | null;
  confidence: number;
  band: ConfidenceBand;
  gates: QualificationGate[];
  failed_gates: GateName[];
  reasons: string[];
  best_candidate: BestCandidate | null;
}

export interface MarketNarrative {
  tone: string; // "bullish" | "bearish" | "neutral"
  headline: string;
  statements: string[];
}

export interface MarketDominance {
  control: ControllingSide;
  buyers_pct: number;
  writers_pct: number;
  ce_dominance: string; // "Strong" | "Balanced" | "Weak"
  pe_dominance: string;
  control_shift_from: string;
  control_shift_to: string;
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

export interface ParticipationRow {
  rank: number;
  strike: string;
  option_type: OptionType;
  classification: Classification | null;
  oi_change: number;
  oi_change_pct: number | null;
  premium_change_pct: number | null;
  volume_change_pct: number | null;
}

export interface StrikeHistoryPoint {
  captured_at: string;
  oi: number;
  oi_change: number;
  oi_change_pct: number | null;
  premium: string;
  premium_change: string;
  premium_change_pct: number | null;
  volume: number;
  volume_change: number;
  volume_change_pct: number | null;
  classification: Classification | null;
}

export interface StrikeHistory {
  strike: string;
  option_type: OptionType;
  points: StrikeHistoryPoint[];
}

export interface EngineStatus {
  healthy: boolean;
  pipeline_runtime_ms: number | null;
  data_age_seconds: number | null;
}

export type ConnectionState =
  | "connected"
  | "connecting"
  | "session_expired"
  | "authentication_failed"
  | "not_connected";

export type AuthStatus = "CONNECTED" | "NOT_AUTHENTICATED";
export type DataSource = "fyers" | "simulator" | "none";

export interface DashboardResponse {
  connection_state: ConnectionState;
  authentication: AuthStatus;
  data_source: DataSource;
  market: MarketSection;
  narrative: MarketNarrative | null;
  dominance: MarketDominance | null;
  qualification: TradeQualification | null;
  participation: ParticipationRow[];
  context: MarketContext | null;
  ce_pe: CePeComparison | null;
  option_chain: OptionChainRow[];
  engine: EngineStatus;
}
