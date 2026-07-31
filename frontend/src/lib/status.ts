// Presentation-only helpers for the decision cards. These derive display state
// from fields the API already provides — they never compute or re-rank market
// values. The engine decides; this only chooses how to label what it decided.

import type {
  Classification,
  ConfidenceBand,
  OptionType,
  TradeQualification,
} from "@/types/dashboard";

export type TradeStatus = "QUALIFIED" | "WATCHING" | "NO_TRADE";

/** The strike currently in focus, whether qualified or merely being watched. */
export interface FocusStrike {
  strike: string;
  option_type: OptionType;
  classification: Classification;
}

/**
 * Derive the headline status from existing qualification fields:
 *   - a qualified trade                       -> QUALIFIED
 *   - not qualified but a candidate exists    -> WATCHING
 *   - nothing to watch                        -> NO_TRADE
 */
export function deriveStatus(q: TradeQualification): TradeStatus {
  if (q.qualified) return "QUALIFIED";
  if (q.best_candidate) return "WATCHING";
  return "NO_TRADE";
}

/**
 * The strike MIOS is focused on: the qualified strike when qualified, otherwise
 * the best candidate it is watching. Null only when there is nothing at all.
 */
export function focusStrike(q: TradeQualification): FocusStrike | null {
  if (q.qualified && q.strike && q.option_type && q.classification) {
    return {
      strike: q.strike,
      option_type: q.option_type,
      classification: q.classification,
    };
  }
  if (q.best_candidate) {
    return {
      strike: q.best_candidate.strike,
      option_type: q.best_candidate.option_type,
      classification: q.best_candidate.classification,
    };
  }
  return null;
}

export const STATUS_LABEL: Record<TradeStatus, string> = {
  QUALIFIED: "TRADE QUALIFIED",
  WATCHING: "WATCHING",
  NO_TRADE: "NO TRADE",
};

/** Uppercase qualitative badge from the engine's own band (not recomputed). */
export function bandLabel(band: ConfidenceBand): string {
  return band.toUpperCase();
}

export type ChainMark = "qualified" | "watching" | "best" | null;

/**
 * How an option-chain row relates to the current decision, for highlighting:
 *   - the qualified strike        -> "qualified" (🟢)
 *   - the watched best candidate  -> "watching"  (🟡) when no trade is qualified
 *   - the best candidate otherwise-> "best"      (⭐)
 * Matched by strike + option type against fields the API already provides.
 */
export function markFor(
  q: TradeQualification | null,
  strike: string,
  optionType: OptionType,
): ChainMark {
  if (!q) return null;
  const same = (s: string | null, t: OptionType | null) =>
    s === strike && t === optionType;

  if (q.qualified && same(q.strike, q.option_type)) return "qualified";

  const bc = q.best_candidate;
  if (bc && same(bc.strike, bc.option_type)) {
    return q.qualified ? "best" : "watching";
  }
  return null;
}
