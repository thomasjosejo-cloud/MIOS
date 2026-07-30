import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import { rowDomId } from "@/lib/rows";
import type { StrikeRecommendation } from "@/types/dashboard";

export function TopCandidates({
  candidates,
  onSelect,
}: {
  candidates: StrikeRecommendation[];
  onSelect: (rowId: string) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Candidates</CardTitle>
      </CardHeader>
      <CardContent>
        {candidates.length > 0 ? (
          <ul className="divide-y divide-border">
            {candidates.map((c) => (
              <li key={`${c.strike}-${c.option_type}`}>
                <button
                  type="button"
                  onClick={() => onSelect(rowDomId(c.strike, c.option_type))}
                  className="flex w-full items-center justify-between gap-2 py-2 text-left text-sm transition-colors hover:text-accent"
                >
                  <span className="flex items-center gap-2">
                    <span className="font-semibold tabular-nums">{c.strike}</span>
                    <Badge
                      variant={c.option_type === "CE" ? "bullish" : "bearish"}
                    >
                      {c.option_type}
                    </Badge>
                  </span>
                  <span className="text-muted">{labelize(c.classification)}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">No candidates.</p>
        )}
      </CardContent>
    </Card>
  );
}
