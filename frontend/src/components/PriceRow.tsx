import { cn } from "@/lib/utils";
import {
  formatClock,
  formatDecimal,
  formatPercent,
  formatSignedDecimal,
  signOf,
} from "@/lib/format";
import type { GapClassification, MarketSection } from "@/types/dashboard";

// Section 2: the live price line — spot, absolute change, percent change, and
// the opening-gap badge. Colour tracks the real direction of the change and the
// real gap direction; nothing is decorative.

function directionClass(sign: -1 | 0 | 1): string {
  if (sign > 0) return "text-bullish";
  if (sign < 0) return "text-bearish";
  return "text-muted";
}

const GAP_META: Record<
  GapClassification,
  { label: string; tone: "bullish" | "bearish" | "muted" }
> = {
  gap_up: { label: "Gap Up", tone: "bullish" },
  gap_up_marginal: { label: "Gap Up (marginal)", tone: "bullish" },
  flat: { label: "Flat Open", tone: "muted" },
  gap_down_marginal: { label: "Gap Down (marginal)", tone: "bearish" },
  gap_down: { label: "Gap Down", tone: "bearish" },
};

const GAP_TONE_CLASS: Record<"bullish" | "bearish" | "muted", string> = {
  bullish: "border-bullish/40 bg-bullish/10 text-bullish",
  bearish: "border-bearish/40 bg-bearish/10 text-bearish",
  muted: "border-border bg-card text-muted",
};

/** The opening-gap badge — omitted entirely when no gap has been captured. */
function GapBadge({
  classification,
  pct,
}: {
  classification: GapClassification | null;
  pct: number | null;
}) {
  if (classification === null) return null;
  const meta = GAP_META[classification];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border-[0.5px] px-2 py-0.5 text-[11px] font-semibold",
        GAP_TONE_CLASS[meta.tone],
      )}
    >
      {meta.label}
      {pct !== null && (
        <span className="tabular-nums font-medium">{formatPercent(pct)}</span>
      )}
    </span>
  );
}

export function PriceRow({
  market,
  gapClassification,
  gapPct,
}: {
  market: MarketSection;
  gapClassification: GapClassification | null;
  gapPct: number | null;
}) {
  const changeSign = signOf(market.change);

  return (
    <section id="price" className="scroll-mt-16 py-1">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted">
          NIFTY
        </span>
        <span className="text-3xl font-bold tabular-nums text-foreground">
          {formatDecimal(market.spot)}
        </span>
        <span
          className={cn(
            "text-base font-semibold tabular-nums",
            directionClass(changeSign),
          )}
        >
          {formatSignedDecimal(market.change)}
        </span>
        <span
          className={cn(
            "text-sm font-medium tabular-nums",
            directionClass(changeSign),
          )}
        >
          {formatPercent(market.change_percent)}
        </span>
        <span className="ml-auto flex items-center gap-2">
          <GapBadge classification={gapClassification} pct={gapPct} />
        </span>
      </div>
      <div className="mt-0.5 text-[11px] text-muted">
        Updated {formatClock(market.updated_at)}
      </div>
    </section>
  );
}
