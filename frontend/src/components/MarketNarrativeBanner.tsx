import { cn } from "@/lib/utils";
import type { MarketNarrative } from "@/types/dashboard";

// Plain-language story rendered at the very top of the dashboard. Every word
// comes from the API's narrative — no frontend logic beyond picking a tone
// colour for the frame.
const TONE_FRAME: Record<string, string> = {
  bullish: "border-bullish/40 bg-bullish/5",
  bearish: "border-bearish/40 bg-bearish/5",
  neutral: "border-border bg-card",
};

export function MarketNarrativeBanner({
  narrative,
}: {
  narrative: MarketNarrative | null;
}) {
  const frame = narrative ? (TONE_FRAME[narrative.tone] ?? TONE_FRAME.neutral) : TONE_FRAME.neutral;

  return (
    <section
      id="narrative"
      className={cn("scroll-mt-16 rounded-lg border-2 p-5", frame)}
    >
      <div className="text-xs font-semibold uppercase tracking-widest text-muted">
        Market Narrative
      </div>
      <p className="mt-2 text-lg font-medium leading-relaxed text-foreground">
        {narrative ? narrative.headline : "Awaiting market data…"}
      </p>
    </section>
  );
}
