import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { ControllingSide, MarketDominance } from "@/types/dashboard";

// Who controls the market and why, straight from the existing CE/PE analysis.
// No values are invented or recomputed: control, the buyer/writer split, the
// CE/PE strength, and the shift all come from the API. This card only orders
// them so the trader reads the conclusion first, then the supporting factors.

function controlTone(side: ControllingSide): string {
  if (side === "bulls") return "text-bullish";
  if (side === "bears") return "text-bearish";
  return "text-muted";
}

function strengthTone(value: string): string {
  if (value === "Strong") return "text-bullish";
  if (value === "Weak") return "text-bearish";
  return "text-muted";
}

function Factor({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between py-1.5 text-sm">
      <span className="text-muted">{label}</span>
      <span className="font-medium">{children}</span>
    </div>
  );
}

export function MarketDominanceCard({
  dominance,
}: {
  dominance: MarketDominance | null;
}) {
  return (
    <Card id="dominance" className="scroll-mt-16">
      <CardHeader>
        <CardTitle>Market Dominance</CardTitle>
      </CardHeader>
      <CardContent>
        {dominance ? (
          <div className="space-y-4">
            {/* Conclusion first: who controls, and the shift into it. */}
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
                Control
              </div>
              <div className="mt-0.5 flex items-baseline justify-between">
                <span
                  className={cn(
                    "text-2xl font-extrabold tracking-tight",
                    controlTone(dominance.control),
                  )}
                >
                  {labelize(dominance.control).toUpperCase()}
                </span>
                <span className="text-xs text-muted">
                  {dominance.control_shift_from} → {dominance.control_shift_to}
                </span>
              </div>
            </div>

            {/* Supporting factor 1: participation split. */}
            <div>
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-bullish">
                  Buyers {dominance.buyers_pct}%
                </span>
                <span className="text-bearish">
                  Writers {dominance.writers_pct}%
                </span>
              </div>
              <div className="flex h-2 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full bg-bullish"
                  style={{ width: `${dominance.buyers_pct}%` }}
                  aria-hidden
                />
                <div
                  className="h-full bg-bearish"
                  style={{ width: `${dominance.writers_pct}%` }}
                  aria-hidden
                />
              </div>
            </div>

            {/* Supporting factor 2: which side is stronger. */}
            <div className="divide-y divide-border border-t border-border pt-1">
              <Factor label="Call side (CE)">
                <span className={strengthTone(dominance.ce_dominance)}>
                  {dominance.ce_dominance}
                </span>
              </Factor>
              <Factor label="Put side (PE)">
                <span className={strengthTone(dominance.pe_dominance)}>
                  {dominance.pe_dominance}
                </span>
              </Factor>
            </div>
          </div>
        ) : (
          <p className="py-2 text-sm text-muted">No dominance data yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
