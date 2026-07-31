import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatPercent, labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Classification, OptionType, ParticipationRow } from "@/types/dashboard";

// Participation Radar — answers "which strikes deserve attention right now?".
// Ranking and every value come from the backend (Radar engine's OI-addition
// order + the Option Engine's percentage changes). The frontend only renders,
// and drives strike selection when a row is clicked.

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

export interface SelectedStrike {
  strike: string;
  option_type: OptionType;
}

export function ParticipationRadar({
  rows,
  selected,
  onSelect,
}: {
  rows: ParticipationRow[];
  selected: SelectedStrike | null;
  onSelect: (s: SelectedStrike) => void;
}) {
  const maxOi = rows.reduce((m, r) => Math.max(m, Math.abs(r.oi_change_pct ?? 0)), 0);

  return (
    <Card id="participation" className="scroll-mt-16 overflow-hidden">
      <CardHeader>
        <CardTitle>Participation Radar</CardTitle>
        <span className="text-xs text-muted">Strongest fresh OI · click to inspect</span>
      </CardHeader>

      {rows.length === 0 ? (
        <p className="px-4 py-6 text-sm text-muted">No participation yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border text-left text-[11px] uppercase tracking-wider text-muted">
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">Strike</th>
                <th className="px-3 py-2 font-medium">Classification</th>
                <th className="px-3 py-2 text-right font-medium">OI %</th>
                <th className="px-3 py-2 text-right font-medium">Prem %</th>
                <th className="px-3 py-2 text-right font-medium">Vol %</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const isSelected =
                  selected?.strike === row.strike &&
                  selected?.option_type === row.option_type;
                const width = maxOi
                  ? `${(Math.abs(row.oi_change_pct ?? 0) / maxOi) * 100}%`
                  : "0%";
                return (
                  <tr
                    key={`${row.strike}-${row.option_type}`}
                    onClick={() =>
                      onSelect({ strike: row.strike, option_type: row.option_type })
                    }
                    className={cn(
                      "cursor-pointer border-b border-border/60 tabular-nums transition-colors",
                      isSelected ? "bg-accent/15" : "hover:bg-border/40",
                    )}
                  >
                    <td className="px-3 py-2 font-semibold text-muted">{row.rank}</td>
                    <td className="whitespace-nowrap px-3 py-2">
                      <span className="mr-2 font-semibold">{row.strike}</span>
                      <Badge
                        variant={row.option_type === "CE" ? "bullish" : "bearish"}
                      >
                        {row.option_type}
                      </Badge>
                    </td>
                    <td className={cn("px-3 py-2", classTone(row.classification))}>
                      {row.classification ? labelize(row.classification) : "—"}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center justify-end gap-2">
                        <span className="hidden h-1 w-16 overflow-hidden rounded-full bg-border sm:block">
                          <span
                            className="block h-full bg-accent"
                            style={{ width }}
                            aria-hidden
                          />
                        </span>
                        <span
                          className={cn(
                            "w-16 text-right font-semibold",
                            pctTone(row.oi_change_pct),
                          )}
                        >
                          {formatPercent(row.oi_change_pct)}
                        </span>
                      </div>
                    </td>
                    <td className={cn("px-3 py-2 text-right", pctTone(row.premium_change_pct))}>
                      {formatPercent(row.premium_change_pct)}
                    </td>
                    <td className={cn("px-3 py-2 text-right", pctTone(row.volume_change_pct))}>
                      {formatPercent(row.volume_change_pct)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
