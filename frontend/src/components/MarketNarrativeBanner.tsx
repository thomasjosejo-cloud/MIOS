import { cn } from "@/lib/utils";
import type { MarketNarrative } from "@/types/dashboard";

// Plain-language story rendered at the very top of the dashboard. Every word
// comes from the API's narrative — the frontend only styles it (tone rail and
// hierarchy); it never rewrites or invents the text.

// The background tint tracks the narrative's real tone — bullish green, bearish
// red, neutral muted. A tint, not a gradient; colour follows genuine state.
const TONE: Record<string, { surface: string; dot: string; label: string }> = {
  bullish: {
    surface: "border-bullish/40 bg-bullish/10",
    dot: "text-bullish",
    label: "Bullish",
  },
  bearish: {
    surface: "border-bearish/40 bg-bearish/10",
    dot: "text-bearish",
    label: "Bearish",
  },
  neutral: {
    surface: "border-border bg-card",
    dot: "text-muted",
    label: "Neutral",
  },
};

export function MarketNarrativeBanner({
  narrative,
}: {
  narrative: MarketNarrative | null;
}) {
  const tone = narrative ? (TONE[narrative.tone] ?? TONE.neutral) : TONE.neutral;

  return (
    <section
      id="narrative"
      className={cn(
        "scroll-mt-16 rounded-xl border-[0.5px] px-4 py-4",
        tone.surface,
      )}
    >
      <div className="flex items-center gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted">
          Market Narrative
        </span>
        {narrative && (
          <span
            className={cn(
              "text-[11px] font-semibold uppercase tracking-wide",
              tone.dot,
            )}
          >
            · {tone.label}
          </span>
        )}
      </div>
      <p className="mt-1.5 text-[1.05rem] font-medium leading-relaxed text-foreground">
        {narrative ? narrative.headline : "Awaiting market data…"}
      </p>
    </section>
  );
}
