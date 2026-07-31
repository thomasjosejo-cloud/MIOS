import { ClassificationChip } from "@/components/ClassificationChip";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { SelectedStrike } from "@/components/ParticipationRadar";
import { useStrikeHistory } from "@/hooks/useStrikeHistory";
import { formatClock, formatInt, formatPercent } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { StrikeHistoryPoint } from "@/types/dashboard";

// Strike Evolution — how the selected strike has developed, using only the
// historical series the backend returns. The frontend renders the progression;
// it does not infer trend verdicts or compute any value.

function pctTone(value: number | null): string {
  if (value === null) return "text-muted";
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted";
}

function Empty({ title, hint }: { title: string; hint: string }) {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center px-6 text-center">
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="mt-1 max-w-xs text-xs text-muted">{hint}</p>
    </div>
  );
}

/** A minimal OI sparkline — pure rendering of the returned series. */
function Sparkline({ points }: { points: StrikeHistoryPoint[] }) {
  const ois = points.map((p) => p.oi);
  const min = Math.min(...ois);
  const max = Math.max(...ois);
  const span = max - min || 1;
  const w = 100;
  const h = 32;
  const coords = points.map((p, i) => {
    const x = points.length > 1 ? (i / (points.length - 1)) * w : 0;
    const y = h - ((p.oi - min) / span) * h;
    return [x, y] as const;
  });
  const line = coords
    .map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`)
    .join(" ");
  const area = `${line} L${w},${h} L0,${h} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className="h-9 w-full" aria-hidden>
      <path d={area} fill="#3B82F6" fillOpacity="0.12" />
      <path d={line} fill="none" stroke="#3B82F6" strokeWidth="1.5" />
    </svg>
  );
}

export function StrikeEvolution({ selected }: { selected: SelectedStrike | null }) {
  const { data, isLoading } = useStrikeHistory(selected);
  const points = data?.points ?? [];
  const latest = points.at(-1);

  return (
    <Card id="strike-evolution" className="scroll-mt-16 flex h-full flex-col overflow-hidden">
      <CardHeader>
        <CardTitle>Strike Evolution</CardTitle>
        {selected && (
          <span className="flex items-center gap-2 text-sm">
            <span className="font-bold tabular-nums">{selected.strike}</span>
            <Badge variant={selected.option_type === "CE" ? "bullish" : "bearish"}>
              {selected.option_type}
            </Badge>
          </span>
        )}
      </CardHeader>

      {!selected ? (
        <Empty
          title="No strike selected"
          hint="Click a strike in Participation Radar to see how its participation has evolved."
        />
      ) : isLoading && points.length === 0 ? (
        <Empty title="Loading history…" hint="Fetching this strike's snapshots." />
      ) : points.length === 0 ? (
        <Empty
          title="No historical evolution available yet"
          hint="History will populate as snapshots are collected for this strike."
        />
      ) : (
        <div className="flex flex-1 flex-col px-4 pb-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-[11px] uppercase tracking-wider text-muted">
                Current Classification
              </div>
              <div className="mt-0.5">
                <ClassificationChip classification={latest?.classification ?? null} />
              </div>
            </div>
            <div className="w-40">
              <div className="text-right text-[11px] uppercase tracking-wider text-muted">
                Open interest
              </div>
              <Sparkline points={points} />
            </div>
          </div>

          <div className="mb-1 text-[11px] uppercase tracking-wider text-muted">
            Evolution
          </div>
          <div className="max-h-72 overflow-auto rounded-md border border-border">
            <table className="w-full border-collapse text-sm">
              <thead className="sticky top-0 bg-card">
                <tr className="border-b border-border text-left text-[11px] uppercase tracking-wider text-muted">
                  <th className="px-2.5 py-2 font-medium">Time</th>
                  <th className="px-2.5 py-2 text-right font-medium">OI</th>
                  <th className="px-2.5 py-2 text-right font-medium">OI %</th>
                  <th className="px-2.5 py-2 text-right font-medium">Prem %</th>
                  <th className="px-2.5 py-2 text-right font-medium">Vol %</th>
                  <th className="px-2.5 py-2 font-medium">Classification</th>
                </tr>
              </thead>
              <tbody>
                {[...points].reverse().map((p, i) => (
                  <tr key={i} className="border-b border-border/60 tabular-nums last:border-0">
                    <td className="whitespace-nowrap px-2.5 py-1.5 text-muted">
                      {formatClock(p.captured_at)}
                    </td>
                    <td className="px-2.5 py-1.5 text-right text-muted">
                      {formatInt(p.oi)}
                    </td>
                    <td className={cn("px-2.5 py-1.5 text-right", pctTone(p.oi_change_pct))}>
                      {formatPercent(p.oi_change_pct)}
                    </td>
                    <td className={cn("px-2.5 py-1.5 text-right", pctTone(p.premium_change_pct))}>
                      {formatPercent(p.premium_change_pct)}
                    </td>
                    <td className={cn("px-2.5 py-1.5 text-right", pctTone(p.volume_change_pct))}>
                      {formatPercent(p.volume_change_pct)}
                    </td>
                    <td className="px-2.5 py-1.5">
                      <ClassificationChip classification={p.classification} />
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
