import type { DashboardResponse } from "@/types/dashboard";

/** A representative healthy dashboard payload for tests. */
export const dashboardFixture: DashboardResponse = {
  market: {
    spot: "25184.25",
    change: "86.25",
    change_percent: 0.34,
    status: "LIVE",
    updated_at: "2026-01-01T09:42:15+00:00",
  },
  recommendation: {
    best_ce: {
      strike: "25150",
      option_type: "CE",
      classification: "long_buildup",
      evidence: [
        "OI ↑ 18.0%",
        "Premium ↑ 9.0%",
        "Volume ↑ 34.0%",
        "Buyers dominant.",
        "Structure confirms breakout.",
      ],
      reason: "Fresh long positions are being added.",
    },
    best_pe: null,
    top_candidates: [
      {
        strike: "25150",
        option_type: "CE",
        classification: "long_buildup",
        evidence: ["OI ↑ 18.0%"],
        reason: "Fresh long positions.",
      },
      {
        strike: "25200",
        option_type: "CE",
        classification: "short_covering",
        evidence: ["OI ↓ 4.0%"],
        reason: "Shorts covering.",
      },
    ],
    no_trade: { no_trade: false, reasons: [] },
  },
  no_trade: { no_trade: false, reasons: [] },
  context: {
    controlling_side: "bulls",
    dominant_participant: "buyers",
    momentum: "increasing",
    momentum_strengthening: true,
    momentum_weakening: false,
    structure_trend: "uptrend",
    structure_validates_options: true,
    contradiction: null,
    immediate_support: "25000",
    immediate_resistance: "25200",
    statements: ["Bulls control the market."],
    evidence: ["Net CE OI change: +12,000"],
  },
  ce_pe: {
    stronger_side: "CE",
    writer_active_strikes: ["25000"],
    buyer_active_strikes: ["25150"],
    control_shifting: false,
    shift_description: null,
    important_strikes: ["25150"],
    evidence: ["Net CE OI change: +12,000"],
  },
  top_candidates: [
    {
      strike: "25150",
      option_type: "CE",
      classification: "long_buildup",
      evidence: ["OI ↑ 18.0%"],
      reason: "Fresh long positions.",
    },
    {
      strike: "25200",
      option_type: "CE",
      classification: "short_covering",
      evidence: ["OI ↓ 4.0%"],
      reason: "Shorts covering.",
    },
  ],
  option_chain: [
    {
      strike: "25150",
      option_type: "CE",
      premium: "142.50",
      oi: 40911,
      oi_change: 1400,
      volume: 18076,
      classification: "long_buildup",
      unusual_flags: ["oi_change", "volume_change"],
      recommendation_flag: true,
    },
    {
      strike: "25200",
      option_type: "CE",
      premium: "98.10",
      oi: 30250,
      oi_change: -800,
      volume: 9021,
      classification: "short_covering",
      unusual_flags: [],
      recommendation_flag: true,
    },
    {
      strike: "25000",
      option_type: "PE",
      premium: "88.25",
      oi: 51200,
      oi_change: 2600,
      volume: 22110,
      classification: "short_buildup",
      unusual_flags: ["oi_velocity"],
      recommendation_flag: false,
    },
  ],
  engine: {
    healthy: true,
    pipeline_runtime_ms: 1.42,
    data_age_seconds: 0.6,
  },
};

/** A no-trade payload with a ranging, trendless market. */
export const noTradeFixture: DashboardResponse = {
  ...dashboardFixture,
  recommendation: {
    best_ce: null,
    best_pe: null,
    top_candidates: [],
    no_trade: {
      no_trade: true,
      reasons: [
        "No HH-HL or LH-LL structure; price action lacks a defined trend.",
        "Price is inside a range, with no breakout or breakdown.",
      ],
    },
  },
  no_trade: {
    no_trade: true,
    reasons: [
      "No HH-HL or LH-LL structure; price action lacks a defined trend.",
      "Price is inside a range, with no breakout or breakdown.",
    ],
  },
  top_candidates: [],
};
