import { ChevronRight, TriangleAlert } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { MarketContext } from "@/types/dashboard";

function Row({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="flex items-center justify-between py-1.5 text-sm">
      <span className="text-muted">{label}</span>
      <span className={cn("font-medium", tone ?? "text-foreground")}>{value}</span>
    </div>
  );
}

function controlTone(side: MarketContext["controlling_side"]): string {
  if (side === "bulls") return "text-bullish";
  if (side === "bears") return "text-bearish";
  return "text-muted";
}

function momentumGlyph(m: MarketContext["momentum"]): string {
  if (m === "increasing") return "↑";
  if (m === "decreasing") return "↓";
  return "→";
}

export function MarketContextCard({ context }: { context: MarketContext | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Market Context</CardTitle>
      </CardHeader>
      <CardContent>
        {context ? (
          <div className="divide-y divide-border">
            <Row
              label="Control"
              value={labelize(context.controlling_side)}
              tone={controlTone(context.controlling_side)}
            />
            <Row label="Trend" value={labelize(context.structure_trend)} />
            <Row
              label="Momentum"
              value={`${labelize(context.momentum)} ${momentumGlyph(context.momentum)}`}
            />
            <Row
              label="Structure"
              value={
                context.structure_validates_options ? "Validates" : "Diverges"
              }
              tone={
                context.structure_validates_options
                  ? "text-bullish"
                  : "text-bearish"
              }
            />
          </div>
        ) : (
          <p className="py-2 text-sm text-muted">No context yet.</p>
        )}

        {/* The contradiction is the single most decision-relevant fact MIOS
            produces — often the *reason* a trade is not qualifying — so it gets
            its own callout rather than a flat "Yes" row. Rendered verbatim. */}
        {context?.contradiction && (
          <div className="mt-3 rounded-md border-l-2 border-bearish bg-bearish/10 p-3">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-bearish">
              <TriangleAlert className="h-3.5 w-3.5" aria-hidden />
              Contradiction
            </div>
            <p className="mt-1 text-sm leading-relaxed text-foreground">
              {context.contradiction}
            </p>
          </div>
        )}

        {/* The engine's factual evidence lines, one click away — secondary
            detail that backs the summary above without competing with it. */}
        {context && context.evidence.length > 0 && (
          <details className="group mt-3">
            <summary className="flex cursor-pointer select-none items-center gap-1 text-xs text-muted transition-colors hover:text-foreground">
              <ChevronRight
                className="h-3.5 w-3.5 transition-transform group-open:rotate-90"
                aria-hidden
              />
              Evidence ({context.evidence.length})
            </summary>
            <ul className="mt-2 space-y-1 pl-1">
              {context.evidence.map((line, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-muted">
                  <span
                    className="mt-1 h-1 w-1 shrink-0 rounded-full bg-muted"
                    aria-hidden
                  />
                  <span className="text-foreground/80">{line}</span>
                </li>
              ))}
            </ul>
          </details>
        )}
      </CardContent>
    </Card>
  );
}
