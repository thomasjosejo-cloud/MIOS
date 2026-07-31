import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MarketNarrative } from "@/types/dashboard";

// A permanent market-intelligence card: the "what is happening now" bullet
// lines the narrative engine produces. Always visible so the trader reads the
// market as a story, not a table. Lines are rendered verbatim from the API.
export function WhatIsHappeningCard({
  narrative,
}: {
  narrative: MarketNarrative | null;
}) {
  const statements = narrative?.statements ?? [];

  return (
    <Card id="what-is-happening" className="scroll-mt-16">
      <CardHeader>
        <CardTitle>What Is Happening Now</CardTitle>
      </CardHeader>
      <CardContent>
        {statements.length > 0 ? (
          <ul className="space-y-2">
            {statements.map((line, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" aria-hidden />
                <span className="text-foreground">{line}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">Awaiting market intelligence…</p>
        )}
      </CardContent>
    </Card>
  );
}
