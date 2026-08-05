import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
  MarketContext,
  StructurePattern,
  SwingLabel,
  SwingPoint,
  TrendDirection,
} from "@/types/dashboard";

// Section 4: at-a-glance structure chips — trend, price-action pattern, and the
// most recent swing labels. Colour tracks whether the structure reads bullish,
// bearish, or neutral. The swing chip is omitted entirely when there are no
// swings (no placeholder), per the brief.

type Tone = "bullish" | "bearish" | "muted";

const TONE_CLASS: Record<Tone, string> = {
  bullish: "border-bullish/40 text-bullish",
  bearish: "border-bearish/40 text-bearish",
  muted: "border-border text-muted",
};

const TREND_TONE: Record<TrendDirection, Tone> = {
  uptrend: "bullish",
  downtrend: "bearish",
  sideways: "muted",
};

const PATTERN_TONE: Record<StructurePattern, Tone> = {
  breakout: "bullish",
  breakdown: "bearish",
  pullback: "muted",
  range: "muted",
};

function Chip({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border-[0.5px] px-2.5 py-1 text-xs font-semibold",
        TONE_CLASS[tone],
      )}
    >
      {children}
    </span>
  );
}

const HIGH_LABELS: ReadonlySet<SwingLabel> = new Set<SwingLabel>(["HH", "LH"]);
const LOW_LABELS: ReadonlySet<SwingLabel> = new Set<SwingLabel>(["HL", "LL"]);

/** Most recent high-label and low-label, joined (e.g. "HH · HL"). */
function recentSwingLabel(swings: SwingPoint[]): string | null {
  if (swings.length === 0) return null;
  const lastHigh = [...swings].reverse().find((s) => HIGH_LABELS.has(s.label));
  const lastLow = [...swings].reverse().find((s) => LOW_LABELS.has(s.label));
  const parts = [lastHigh?.label, lastLow?.label].filter(Boolean) as string[];
  return parts.length > 0 ? parts.join(" · ") : null;
}

export function ContextChips({ context }: { context: MarketContext | null }) {
  if (!context) return null;

  const swingLabel = recentSwingLabel(context.swings);

  return (
    <section id="context" className="flex flex-wrap gap-2">
      <Chip tone={TREND_TONE[context.structure_trend]}>
        {labelize(context.structure_trend)}
      </Chip>
      <Chip tone={PATTERN_TONE[context.structure_pattern]}>
        {labelize(context.structure_pattern)}
      </Chip>
      {swingLabel && <Chip tone="muted">{swingLabel}</Chip>}
    </section>
  );
}
