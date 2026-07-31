import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { useStrikeHistory } from "@/hooks/useStrikeHistory";
import { formatClock, formatInt, formatPercent, labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Classification, StrikeHistoryPoint } from "@/types/dashboard";
import type { SelectedStrike } from "@/components/ParticipationRadar";

// Strike Evolution — shows how the selected strike has developed, using only the
// historical series the backend returns. The frontend renders the progression;
// it does not infer trend verdicts or compute any value.

function classTone(c: Classification | null): string {
  switch (c) {
    case "long_buildup":
    case "short_covering":
      return "text-bullish";
    case "short_buildup":
    case "long_unwinding":
      return "text-bearish";
    default:
      return "text-muted";
  }
}

function pctTone(value: number | null): string {
  if (value === null) return "text-muted";
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted";
}

/** A minimal OI sparkline — pure rendering of the returned series. */
function Sparkline({ points }: { points: StrikeHistoryPoint[] }) {
  const ois = points.map((p) => p.oi);
  const min = Math.min(...ois);
  const max = Math.max(...ois);
  const span = max - min || 1;
  const w = 100;
  const h = 28;
  const path = points
    .map((p, i) => {
      const x = points.length > 1 ? (i / (points.length - 1)) * w : 0;
      const y = h - ((p.oi - min) / span) * h;
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      className="h-8 w-full"
      aria-hidden
    >
      <path d={path} fill="none" stroke="#3B82F6" strokeWidth="1.5" />
    </svg>
  );
}

export function StrikeEvolution({ selected }: { selected: SelectedStrike | null }) {
  const { data, isLoading } = useStrikeHistory(selected);
  const points = data?.points ?? [];
  const latest = points.at(-1);

  return (
    <Card id="strike-evolution" className="scroll-mt-16 overflow-hidden">
      <CardHeader>
        <CardTitle>Strike Evolution</CardTitle>
        {selected && (
          <span className="flex items-center gap-2 text-sm">
            <span className="font-semibold tabular-nums">{selected.strike}</span>
            <Badge variant={selected.option_type === "CE" ? "bullish" : "bearish"}>
              {selected.option_type}
            </Badge>
            {latest?.classification && (
              <span className={cn("text-xs", classTone(latest.classification))}>
                {labelize(latest.classification)}
              </span>
            )}
          </span>
        )}
      </CardHeader>

      {!selected ? (
        <p className="px-4 py-6 text-sm text-muted">
          Select a strike in Participation Radar to see how it has evolved.
        </p>
      ) : isLoading && points.length === 0 ? (
        <p className="px-4 py-6 text-sm text-muted">Loading history…</p>
      ) : points.length === 0 ? (
        <p className="px-4 py-6 text-sm text-muted">
          No history captured yet for this strike.
        </p>
      ) : (
        <div className="px-4 pb-4">
          <div className="mb-3 rounded-md border border-border bg-background/40 p-3">
            <div className="mb-1 text-[11px] uppercase tracking-wider text-muted">
              Open interest over time
            </div>
            <Sparkline points={points} />
          </div>
          <div className="max-h-64 overflow-auto">
            <table className="w-full border-collapse text-sm">
              <thead className="sticky top-0 bg-card">
                <tr className="border-b border-border text-left text-[11px] uppercase tracking-wider text-muted">
                  <th className="px-2 py-2 font-medium">Time</th>
                  <th className="px-2 py-2 text-right font-medium">OI</th>
                  <th className="px-2 py-2 text-right font-medium">OI %</th>
                  <th className="px-2 py-2 text-right font-medium">Prem %</th>
                  <th className="px-2 py-2 text-right font-medium">Vol %</th>
                  <th className="px-2 py-2 font-medium">Classification</th>
                </tr>
              </thead>
              <tbody>
                {[...points].reverse().map((p, i) => (
                  <tr key={i} className="border-b border-border/60 tabular-nums">
                    <td className="whitespace-nowrap px-2 py-1.5 text-muted">
                      {formatClock(p.captured_at)}
                    </td>
                    <td className="px-2 py-1.5 text-right text-muted">
                      {formatInt(p.oi)}
                    </td>
                    <td className={cn("px-2 py-1.5 text-right", pctTone(p.oi_change_pct))}>
                      {formatPercent(p.oi_change_pct)}
                    </td>
                    <td className={cn("px-2 py-1.5 text-right", pctTone(p.premium_change_pct))}>
                      {formatPercent(p.premium_change_pct)}
                    </td>
                    <td className={cn("px-2 py-1.5 text-right", pctTone(p.volume_change_pct))}>
                      {formatPercent(p.volume_change_pct)}
                    </td>
                    <td className={cn("px-2 py-1.5", classTone(p.classification))}>
                      {p.classification ? labelize(p.classification) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Card>
  );
}
