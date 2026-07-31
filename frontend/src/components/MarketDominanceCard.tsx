import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { ControllingSide, MarketDominance } from "@/types/dashboard";

// Who controls the market, straight from the existing CE/PE analysis. No values
// are invented: the buyer/writer split and CE/PE dominance come from the API.

function controlTone(side: ControllingSide): string {
  if (side === "bulls") return "text-bullish";
  if (side === "bears") return "text-bearish";
  return "text-muted";
}

function dominanceTone(value: string): string {
  if (value === "Strong") return "text-bullish";
  if (value === "Weak") return "text-bearish";
  return "text-muted";
}

function Row({
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
          <div className="space-y-3">
            <div className="divide-y divide-border">
              <Row label="Control">
                <span className={controlTone(dominance.control)}>
                  {labelize(dominance.control).toUpperCase()}
                </span>
              </Row>
              <Row label="CE Dominance">
                <span className={dominanceTone(dominance.ce_dominance)}>
                  {dominance.ce_dominance}
                </span>
              </Row>
              <Row label="PE Dominance">
                <span className={dominanceTone(dominance.pe_dominance)}>
                  {dominance.pe_dominance}
                </span>
              </Row>
              <Row label="Control Shift">
                <span className="text-foreground">
                  {dominance.control_shift_from} → {dominance.control_shift_to}
                </span>
              </Row>
            </div>

            {/* Buyers vs writers split */}
            <div>
              <div className="mb-1 flex justify-between text-xs text-muted">
                <span>Buyers {dominance.buyers_pct}%</span>
                <span>Writers {dominance.writers_pct}%</span>
              </div>
              <div className="flex h-2 overflow-hidden rounded-full bg-border">
                <div
                  className={cn("h-full bg-bullish")}
                  style={{ width: `${dominance.buyers_pct}%` }}
                  aria-hidden
                />
                <div
                  className={cn("h-full bg-bearish")}
                  style={{ width: `${dominance.writers_pct}%` }}
                  aria-hidden
                />
              </div>
            </div>
          </div>
        ) : (
          <p className="py-2 text-sm text-muted">No dominance data yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
