import { ClassificationChip } from "@/components/ClassificationChip";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { OptionType, ParticipationRow } from "@/types/dashboard";

// Participation Radar — answers "which strikes deserve attention first?".
// Ranking and every value come from the backend (Radar engine's OI-addition
// order + the Option Engine's percentage changes). The frontend only renders
// and drives strike selection when a row is clicked.

export interface SelectedStrike {
  strike: string;
  option_type: OptionType;
}

function pctTone(value: number | null): string {
  if (value === null) return "text-muted";
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted";
}

/** A compact signed magnitude bar + value, centred on zero. */
function PctCell({ value, max }: { value: number | null; max: number }) {
  const magnitude = value === null ? 0 : Math.min(Math.abs(value) / (max || 1), 1);
  const up = (value ?? 0) >= 0;
  return (
    <div className="flex items-center justify-end gap-2">
      <span className="hidden h-1.5 w-14 overflow-hidden rounded-full bg-border sm:block">
        <span
          className={cn("block h-full rounded-full", up ? "bg-bullish" : "bg-bearish")}
          style={{ width: `${magnitude * 100}%` }}
          aria-hidden
        />
      </span>
      <span className={cn("w-16 text-right font-semibold tabular-nums", pctTone(value))}>
        {formatPercent(value)}
      </span>
    </div>
  );
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
  const maxPrem = rows.reduce((m, r) => Math.max(m, Math.abs(r.premium_change_pct ?? 0)), 0);
  const maxVol = rows.reduce((m, r) => Math.max(m, Math.abs(r.volume_change_pct ?? 0)), 0);

  return (
    <Card id="participation" className="scroll-mt-16 overflow-hidden">
      <CardHeader>
        <CardTitle>Participation Radar</CardTitle>
        <span className="text-xs text-muted">Strongest fresh OI · click to inspect</span>
      </CardHeader>

      {rows.length === 0 ? (
        <div className="px-4 py-10 text-center">
          <p className="text-sm font-medium text-foreground">
            No meaningful participation detected yet.
          </p>
          <p className="mt-1 text-xs text-muted">
            Waiting for live market participation to build.
          </p>
        </div>
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
                const isTop = row.rank === 1;
                return (
                  <tr
                    key={`${row.strike}-${row.option_type}`}
                    onClick={() =>
                      onSelect({ strike: row.strike, option_type: row.option_type })
                    }
                    className={cn(
                      "cursor-pointer border-b border-border/60 tabular-nums transition-colors",
                      // Selection wins; the rank-1 row gets a persistent tint.
                      isSelected
                        ? "bg-accent/20 ring-1 ring-inset ring-accent"
                        : isTop
                          ? "bg-bullish/[0.06] hover:bg-bullish/10"
                          : "hover:bg-border/50",
                    )}
                  >
                    <td className="px-3 py-3">
                      <span
                        className={cn(
                          "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                          isTop
                            ? "bg-accent text-white"
                            : "bg-border/70 text-muted",
                        )}
                      >
                        {row.rank}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-3">
                      <span
                        className={cn(
                          "mr-2 font-bold tabular-nums",
                          isTop ? "text-lg text-foreground" : "text-foreground",
                        )}
                      >
                        {row.strike}
                      </span>
                      <Badge
                        variant={row.option_type === "CE" ? "bullish" : "bearish"}
                      >
                        {row.option_type}
                      </Badge>
                    </td>
                    <td className="px-3 py-3">
                      <ClassificationChip classification={row.classification} />
                    </td>
                    <td className="px-3 py-3">
                      <PctCell value={row.oi_change_pct} max={maxOi} />
                    </td>
                    <td className="px-3 py-3">
                      <PctCell value={row.premium_change_pct} max={maxPrem} />
                    </td>
                    <td className="px-3 py-3">
                      <PctCell value={row.volume_change_pct} max={maxVol} />
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
