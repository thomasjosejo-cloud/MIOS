import { ClassificationChip } from "@/components/ClassificationChip";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { OptionType, ParticipationRow } from "@/types/dashboard";

// Participation Radar — the five strike levels around the money (ATM, ATM±1,
// ATM±2), one row per strike with the CE and PE side placed side by side. The
// window is anchored on `atm_strike` from the API and shifts automatically with
// spot. Every value (classification and the OI / premium / volume percentage
// changes) comes straight from the engine's participation output — the frontend
// only selects which strikes to show and renders them.

export interface SelectedStrike {
  strike: string;
  option_type: OptionType;
}

/** How many strikes to show on each side of ATM. */
const ATM_WINDOW = 2;

type SideMap = Partial<Record<OptionType, ParticipationRow>>;

function pctTone(value: number | null): string {
  if (value === null) return "text-muted";
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted";
}

/** The ATM-relative label for an offset k, e.g. 0 -> "ATM", -1 -> "ATM−1". */
function atmLabel(k: number): string {
  if (k === 0) return "ATM";
  return k > 0 ? `ATM+${k}` : `ATM−${-k}`;
}

interface Level {
  offset: number;
  strike: number;
  sides: SideMap;
}

/** The ATM±window strike levels, highest strike first, with their CE/PE rows. */
function buildLevels(
  rows: ParticipationRow[],
  atm: number,
  step: number,
): Level[] {
  const byStrike = new Map<number, SideMap>();
  for (const row of rows) {
    const key = Number(row.strike);
    const sides = byStrike.get(key) ?? {};
    sides[row.option_type] = row;
    byStrike.set(key, sides);
  }

  return offsetRange(ATM_WINDOW).map((offset) => {
    const strike = atm + offset * step;
    return { offset, strike, sides: byStrike.get(strike) ?? {} };
  });
}

/** [w, w-1, …, 0, …, -w] — highest strike (ATM+w) rendered first. */
function offsetRange(window: number): number[] {
  const out: number[] = [];
  for (let k = window; k >= -window; k--) out.push(k);
  return out;
}

/** One metric within a side block: a small label above the signed percentage. */
function Metric({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="text-right">
      <div className="text-[10px] uppercase tracking-wide text-muted">{label}</div>
      <div className={cn("font-semibold tabular-nums", pctTone(value))}>
        {formatPercent(value)}
      </div>
    </div>
  );
}

/** The CE or PE side of a strike: classification + OI/Prem/Vol % changes. */
function SideBlock({
  row,
  optionType,
  isSelected,
  onSelect,
}: {
  row: ParticipationRow | undefined;
  optionType: OptionType;
  isSelected: boolean;
  onSelect: (s: SelectedStrike) => void;
}) {
  const accent = optionType === "CE" ? "text-bullish" : "text-bearish";

  if (!row) {
    return (
      <div className="rounded-md border border-dashed border-border/60 px-3 py-2.5">
        <div className={cn("text-[11px] font-semibold", accent)}>{optionType}</div>
        <div className="mt-1 text-xs text-muted">No participation</div>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onSelect({ strike: row.strike, option_type: optionType })}
      className={cn(
        "w-full rounded-md border px-3 py-2.5 text-left transition-colors",
        isSelected
          ? "border-accent bg-accent/15 ring-1 ring-inset ring-accent"
          : "border-border/60 hover:bg-border/40",
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className={cn("text-[11px] font-semibold", accent)}>{optionType}</span>
        <ClassificationChip classification={row.classification} />
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2">
        <Metric label="OI" value={row.oi_change_pct} />
        <Metric label="Prem" value={row.premium_change_pct} />
        <Metric label="Vol" value={row.volume_change_pct} />
      </div>
    </button>
  );
}

export function ParticipationRadar({
  rows,
  atmStrike,
  strikeStep,
  selected,
  onSelect,
}: {
  rows: ParticipationRow[];
  atmStrike: string | null;
  strikeStep: number;
  selected: SelectedStrike | null;
  onSelect: (s: SelectedStrike) => void;
}) {
  const atm = atmStrike === null ? null : Number(atmStrike);
  const hasAtm = atm !== null && !Number.isNaN(atm);
  const levels = hasAtm ? buildLevels(rows, atm, strikeStep) : [];

  const isSideSelected = (strike: number, optionType: OptionType): boolean =>
    selected !== null &&
    Number(selected.strike) === strike &&
    selected.option_type === optionType;

  return (
    <Card id="participation" className="scroll-mt-16 overflow-hidden">
      <CardHeader>
        <CardTitle>Participation Radar</CardTitle>
        <span className="text-xs text-muted">
          {hasAtm
            ? `ATM ${atmStrike} ± ${ATM_WINDOW} strikes · click a side to inspect`
            : "Strikes around the money · click a side to inspect"}
        </span>
      </CardHeader>

      {!hasAtm || rows.length === 0 ? (
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
                <th className="px-3 py-2 font-medium">Strike</th>
                <th className="px-3 py-2 font-medium">CE</th>
                <th className="px-3 py-2 font-medium">PE</th>
              </tr>
            </thead>
            <tbody>
              {levels.map((level) => {
                const isAtm = level.offset === 0;
                return (
                  <tr
                    key={level.offset}
                    className={cn(
                      "border-b border-border/60 align-top",
                      isAtm && "bg-accent/[0.06]",
                    )}
                  >
                    <td className="whitespace-nowrap px-3 py-3">
                      <div className="font-bold tabular-nums text-foreground">
                        {level.strike}
                      </div>
                      <div
                        className={cn(
                          "text-[11px] uppercase tracking-wide",
                          isAtm ? "font-semibold text-accent" : "text-muted",
                        )}
                      >
                        {atmLabel(level.offset)}
                      </div>
                    </td>
                    <td className="px-2 py-2.5">
                      <SideBlock
                        row={level.sides.CE}
                        optionType="CE"
                        isSelected={isSideSelected(level.strike, "CE")}
                        onSelect={onSelect}
                      />
                    </td>
                    <td className="px-2 py-2.5">
                      <SideBlock
                        row={level.sides.PE}
                        optionType="PE"
                        isSelected={isSideSelected(level.strike, "PE")}
                        onSelect={onSelect}
                      />
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
