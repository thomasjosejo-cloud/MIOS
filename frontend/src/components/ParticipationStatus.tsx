import { ClassificationChip } from "@/components/ClassificationChip";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatPercent } from "@/lib/format";
import { focusStrike } from "@/lib/status";
import { cn } from "@/lib/utils";
import type {
  ControllingSide,
  ParticipationRow,
  TradeQualification,
} from "@/types/dashboard";

// Participation Status — the live participation of the strike MIOS currently
// recommends, sat directly under the Recommended Trade card. Every value is
// read from fields the API already provides: the recommended strike's row in
// the participation feed (classification + OI / premium / volume % changes) and
// the market's controlling side. Nothing is recomputed here.

const CONTROL: Record<ControllingSide, { label: string; tone: string }> = {
  bulls: { label: "Bulls", tone: "text-bullish" },
  bears: { label: "Bears", tone: "text-bearish" },
  neutral: { label: "Neutral", tone: "text-muted" },
};

function pctTone(value: number | null): string {
  if (value === null) return "text-muted";
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted";
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
      {children}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number | null }) {
  return (
    <div>
      <SectionLabel>{label}</SectionLabel>
      <div className={cn("mt-1 text-lg font-bold tabular-nums", pctTone(value))}>
        {formatPercent(value)}
      </div>
    </div>
  );
}

export function ParticipationStatus({
  qualification,
  participation,
  control,
}: {
  qualification: TradeQualification | null;
  participation: ParticipationRow[];
  control: ControllingSide | null;
}) {
  const focus = qualification ? focusStrike(qualification) : null;

  if (!focus) {
    return (
      <Card id="participation-status" className="scroll-mt-16 p-5">
        <SectionLabel>Participation Status</SectionLabel>
        <p className="mt-3 text-sm text-muted">
          No recommended strike to analyse yet.
        </p>
      </Card>
    );
  }

  // The recommended strike's row in the participation feed, if it is present.
  const row = participation.find(
    (p) =>
      Number(p.strike) === Number(focus.strike) &&
      p.option_type === focus.option_type,
  );
  const classification = row?.classification ?? focus.classification;
  const marketControl = control ? CONTROL[control] : null;

  return (
    <Card id="participation-status" className="scroll-mt-16 p-5">
      <div className="flex items-center justify-between">
        <SectionLabel>Participation Status</SectionLabel>
        <span className="flex items-center gap-2">
          <span className="text-sm font-bold tabular-nums text-foreground">
            {focus.strike}
          </span>
          <Badge variant={focus.option_type === "CE" ? "bullish" : "bearish"}>
            {focus.option_type}
          </Badge>
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-4 sm:grid-cols-3 lg:grid-cols-5">
        <div>
          <SectionLabel>Classification</SectionLabel>
          <div className="mt-1.5">
            <ClassificationChip classification={classification} />
          </div>
        </div>
        <Metric label="OI %" value={row?.oi_change_pct ?? null} />
        <Metric label="Premium %" value={row?.premium_change_pct ?? null} />
        <Metric label="Volume %" value={row?.volume_change_pct ?? null} />
        <div>
          <SectionLabel>Market Control</SectionLabel>
          <div
            className={cn(
              "mt-1 text-lg font-bold",
              marketControl?.tone ?? "text-muted",
            )}
          >
            {marketControl?.label ?? "—"}
          </div>
        </div>
      </div>
    </Card>
  );
}
