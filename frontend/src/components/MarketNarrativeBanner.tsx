import { cn } from "@/lib/utils";
import type { MarketNarrative } from "@/types/dashboard";

// Plain-language story rendered at the very top of the dashboard. Every word
// comes from the API's narrative — the frontend only styles it (tone rail and
// hierarchy); it never rewrites or invents the text.

const TONE: Record<string, { frame: string; rail: string; dot: string; label: string }> = {
  bullish: {
    frame: "border-bullish/30",
    rail: "bg-bullish",
    dot: "text-bullish",
    label: "Bullish",
  },
  bearish: {
    frame: "border-bearish/30",
    rail: "bg-bearish",
    dot: "text-bearish",
    label: "Bearish",
  },
  neutral: {
    frame: "border-border",
    rail: "bg-muted",
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
        "relative scroll-mt-16 overflow-hidden rounded-lg border bg-card pl-5 pr-5 py-4",
        tone.frame,
      )}
    >
      {/* Tone rail — a quiet directional cue, not a decorative gradient. */}
      <span className={cn("absolute inset-y-0 left-0 w-1", tone.rail)} aria-hidden />

      <div className="flex items-center gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted">
          Market Narrative
        </span>
        {narrative && (
          <span className={cn("text-[11px] font-semibold uppercase tracking-wide", tone.dot)}>
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
