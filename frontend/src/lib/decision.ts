// Display-only selection of what to surface in the Recommendation card. These
// pick which engine-provided object to show; they never compute or re-rank.

import type {
  DashboardResponse,
  RecommendationReport,
  StrikeRecommendation,
} from "@/types/dashboard";

export type Action = "BUY" | "NO_TRADE" | "WAITING";

/** The engine never recommends more than a best CE and a best PE; prefer CE. */
export function primaryPick(
  recommendation: RecommendationReport | null,
): StrikeRecommendation | null {
  if (!recommendation) return null;
  return recommendation.best_ce ?? recommendation.best_pe;
}

/** The other side's pick, shown as a secondary line when both exist. */
export function secondaryPick(
  recommendation: RecommendationReport | null,
): StrikeRecommendation | null {
  if (!recommendation) return null;
  if (recommendation.best_ce && recommendation.best_pe) {
    return recommendation.best_pe;
  }
  return null;
}

/** Derive the headline action strictly from engine output. */
export function deriveAction(dashboard: DashboardResponse): Action {
  const { recommendation, no_trade } = dashboard;
  if (!recommendation) return "WAITING";
  if (no_trade?.no_trade ?? recommendation.no_trade.no_trade) return "NO_TRADE";
  return primaryPick(recommendation) ? "BUY" : "NO_TRADE";
}
