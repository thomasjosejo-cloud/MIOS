import type { ReactNode } from "react";

import type { SelectedStrike } from "@/components/ParticipationRadar";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDecimal, formatInt, formatSignedInt, labelize } from "@/lib/format";
import { rowDomId } from "@/lib/rows";
import { type ChainMark, markFor } from "@/lib/status";
import { cn } from "@/lib/utils";
import type {
  Classification,
  OptionChainRow,
  TradeQualification,
} from "@/types/dashboard";

const COLUMNS = [
  "Strike",
  "Type",
  "Premium",
  "OI",
  "OI Δ",
  "Volume",
  "Classification",
  "Unusual",
  "Signal",
] as const;

const MARK: Record<
  Exclude<ChainMark, null>,
  { glyph: string; label: string; row: string }
> = {
  qualified: { glyph: "🟢", label: "Qualified", row: "bg-bullish/10" },
  watching: { glyph: "🟡", label: "Watching", row: "bg-[#E0A82E]/10" },
  best: { glyph: "⭐", label: "Best candidate", row: "bg-accent/10" },
};

function classificationTone(c: Classification | null): string {
  switch (c) {
    case "long_buildup":
      return "text-bullish";
    case "short_covering":
      return "text-bullish";
    case "short_buildup":
      return "text-bearish";
    case "long_unwinding":
      return "text-bearish";
    default:
      return "text-muted";
  }
}

function Cell({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <td className={cn("whitespace-nowrap px-3 py-1.5", className)}>{children}</td>
  );
}

export function OptionChain({
  rows,
  highlightedRowId,
  qualification = null,
  selected = null,
}: {
  rows: OptionChainRow[];
  highlightedRowId: string | null;
  qualification?: TradeQualification | null;
  selected?: SelectedStrike | null;
}) {
  return (
    <Card id="option-chain" className="scroll-mt-16 overflow-hidden">
      <CardHeader>
        <CardTitle>Option Chain</CardTitle>
        <span className="text-xs text-muted">Nearest {rows.length} around ATM</span>
      </CardHeader>
      <div className="max-h-[480px] overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="sticky top-0 z-10 bg-card">
            <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted">
              {COLUMNS.map((c) => (
                <th key={c} className="whitespace-nowrap px-3 py-2 font-medium">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const id = rowDomId(row.strike, row.option_type);
              const mark = markFor(qualification, row.strike, row.option_type);
              const marker = mark ? MARK[mark] : null;
              const isSelected =
                highlightedRowId === id ||
                (selected?.strike === row.strike &&
                  selected?.option_type === row.option_type);
              return (
                <tr
                  key={id}
                  id={id}
                  data-testid={id}
                  className={cn(
                    "scroll-mt-14 border-b border-border/60 tabular-nums transition-colors",
                    marker?.row,
                    isSelected
                      ? "bg-accent/20 ring-2 ring-inset ring-accent"
                      : "hover:bg-border/40",
                  )}
                >
                  <Cell className="font-semibold">{row.strike}</Cell>
                  <Cell
                    className={
                      row.option_type === "CE" ? "text-bullish" : "text-bearish"
                    }
                  >
                    {row.option_type}
                  </Cell>
                  <Cell>{formatDecimal(row.premium)}</Cell>
                  <Cell className="text-muted">{formatInt(row.oi)}</Cell>
                  <Cell
                    className={
                      row.oi_change > 0
                        ? "text-bullish"
                        : row.oi_change < 0
                          ? "text-bearish"
                          : "text-muted"
                    }
                  >
                    {formatSignedInt(row.oi_change)}
                  </Cell>
                  <Cell className="text-muted">{formatInt(row.volume)}</Cell>
                  <Cell className={classificationTone(row.classification)}>
                    {row.classification ? labelize(row.classification) : "—"}
                  </Cell>
                  <Cell>
                    {row.unusual_flags.length > 0 ? (
                      <span className="flex flex-wrap gap-1">
                        {row.unusual_flags.map((f) => (
                          <span
                            key={f}
                            className="rounded bg-accent/15 px-1.5 py-0.5 text-xs text-accent"
                          >
                            {labelize(f)}
                          </span>
                        ))}
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </Cell>
                  <Cell>
                    {marker ? (
                      <span
                        className="inline-flex items-center gap-1.5 text-xs"
                        title={marker.label}
                      >
                        <span aria-hidden>{marker.glyph}</span>
                        <span className="text-muted">{marker.label}</span>
                      </span>
                    ) : isSelected ? (
                      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-accent">
                        <span aria-hidden>◄</span> Inspecting
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </Cell>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
