import { Check, X } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { NoTradeDecision, StrikeRecommendation } from "@/types/dashboard";

/**
 * Renders evidence exactly as provided by the API — the chosen strike's
 * evidence lines, or the no-trade reasons when there is no trade. No frontend
 * logic or calculation; each line is a string straight from the engine.
 */
export function EvidenceCard({
  pick,
  noTrade,
}: {
  pick: StrikeRecommendation | null;
  noTrade: NoTradeDecision | null;
}) {
  const showReasons = !pick && noTrade?.no_trade;
  const items = pick ? pick.evidence : showReasons ? noTrade.reasons : [];

  return (
    <Card id="evidence" className="scroll-mt-16">
      <CardHeader>
        <CardTitle>{showReasons ? "Why No Trade" : "Evidence"}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length > 0 ? (
          <ul className="space-y-2">
            {items.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                {showReasons ? (
                  <X className="mt-0.5 h-4 w-4 shrink-0 text-bearish" aria-hidden />
                ) : (
                  <Check
                    className="mt-0.5 h-4 w-4 shrink-0 text-bullish"
                    aria-hidden
                  />
                )}
                <span className="text-foreground">{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">No evidence yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
