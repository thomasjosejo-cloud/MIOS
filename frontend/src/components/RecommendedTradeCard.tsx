import { Check, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import {
  bandLabel,
  deriveStatus,
  focusStrike,
  STATUS_LABEL,
  type TradeStatus,
} from "@/lib/status";
import { cn } from "@/lib/utils";
import type { SelectedStrike } from "@/components/ParticipationRadar";
import type {
  ConfidenceBand,
  QualificationGate,
  TradeQualification,
} from "@/types/dashboard";

// The primary decision card. It always answers, in order: what strike is MIOS
// watching, can it be traded, how confident is it, why that strike, and what is
// still missing. Every value is rendered from the API's qualification object —
// nothing is computed or invented here.

const STATUS_STYLE: Record<
  TradeStatus,
  { frame: string; pill: string; accent: string }
> = {
  QUALIFIED: {
    frame: "border-bullish/50 bg-bullish/[0.06]",
    pill: "bg-bullish/15 text-bullish",
    accent: "text-bullish",
  },
  WATCHING: {
    frame: "border-[#E0A82E]/40 bg-[#E0A82E]/[0.05]",
    pill: "bg-[#E0A82E]/15 text-[#E0A82E]",
    accent: "text-[#E0A82E]",
  },
  NO_TRADE: {
    frame: "border-border bg-card",
    pill: "bg-bearish/15 text-bearish",
    accent: "text-muted",
  },
};

const BAND_TONE: Record<ConfidenceBand, string> = {
  "Very High": "text-bullish",
  High: "text-bullish",
  Medium: "text-accent",
  Low: "text-bearish",
  "Very Low": "text-bearish",
};

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
      {children}
    </div>
  );
}

function Confidence({
  confidence,
  band,
}: {
  confidence: number;
  band: ConfidenceBand;
}) {
  return (
    <div>
      <SectionLabel>Confidence</SectionLabel>
      <div className="flex items-center gap-3">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-border">
          <div
            className={cn(
              "h-full rounded-full",
              confidence >= 75
                ? "bg-bullish"
                : confidence >= 60
                  ? "bg-accent"
                  : "bg-bearish",
            )}
            style={{ width: `${confidence}%` }}
            aria-hidden
          />
        </div>
        <span className="tabular-nums text-2xl font-bold leading-none text-foreground">
          {confidence}%
        </span>
        <span
          className={cn(
            "rounded px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
            BAND_TONE[band],
            "bg-border/60",
          )}
        >
          {bandLabel(band)}
        </span>
      </div>
    </div>
  );
}

function NeedRow({ gate }: { gate: QualificationGate }) {
  return (
    <li className="flex items-start gap-2 text-sm">
      {gate.passed ? (
        <Check className="mt-0.5 h-4 w-4 shrink-0 text-bullish" aria-hidden />
      ) : (
        <X className="mt-0.5 h-4 w-4 shrink-0 text-muted" aria-hidden />
      )}
      <span className="flex-1">
        <span
          className={cn(
            "font-medium",
            gate.passed ? "text-foreground" : "text-muted",
          )}
        >
          {gate.name}
        </span>
        {gate.mandatory && !gate.passed && (
          <span className="ml-1.5 text-[11px] uppercase tracking-wide text-bearish">
            required
          </span>
        )}
        <span className="block text-xs text-muted">{gate.reason}</span>
      </span>
    </li>
  );
}

export function RecommendedTradeCard({
  qualification,
  inspecting = null,
}: {
  qualification: TradeQualification | null;
  inspecting?: SelectedStrike | null;
}) {
  if (!qualification) {
    return (
      <Card id="qualification" className="scroll-mt-16 border-[0.5px] p-5">
        <SectionLabel>Recommended Trade</SectionLabel>
        <p className="mt-3 text-sm text-muted">Awaiting engine data…</p>
      </Card>
    );
  }

  const status = deriveStatus(qualification);
  const style = STATUS_STYLE[status];
  const focus = focusStrike(qualification);

  return (
    <Card
      id="qualification"
      className={cn("scroll-mt-16 border-[0.5px] p-5", style.frame)}
    >
      {/* Header: title + status pill */}
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted">
          Recommended Trade
        </span>
        <div className="flex items-center gap-2">
          {inspecting && (
            <span className="hidden items-center gap-1 rounded-full border border-accent/40 px-2 py-0.5 text-[11px] text-accent sm:inline-flex">
              Inspecting {inspecting.strike} {inspecting.option_type}
            </span>
          )}
          <span
            className={cn(
              "rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
              style.pill,
            )}
          >
            {STATUS_LABEL[status]}
          </span>
        </div>
      </div>

      {/* Focus strike — always shown when one exists (qualified or watched) */}
      {focus ? (
        <div className="mt-3 flex items-baseline gap-2.5">
          <span className="tabular-nums text-[2.75rem] font-extrabold leading-none text-foreground">
            {focus.strike}
          </span>
          <Badge variant={focus.option_type === "CE" ? "bullish" : "bearish"}>
            {focus.option_type}
          </Badge>
          <span className="text-sm text-muted">
            {labelize(focus.classification)}
          </span>
        </div>
      ) : (
        <p className="mt-3 text-sm text-muted">
          No strike in focus — MIOS is standing aside until positioning appears.
        </p>
      )}

      {/* Confidence: percentage + qualitative band */}
      <div className="mt-4">
        <Confidence
          confidence={qualification.confidence}
          band={qualification.band}
        />
      </div>

      {/* Why this strike — factual evidence, shown whenever the engine has it */}
      {qualification.reasons.length > 0 && (
        <div className="mt-4 border-t border-border pt-4">
          <SectionLabel>Why This Strike?</SectionLabel>
          <ul className="grid gap-x-4 gap-y-1.5 sm:grid-cols-2">
            {qualification.reasons.map((line, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Check
                  className="mt-0.5 h-3.5 w-3.5 shrink-0 text-bullish"
                  aria-hidden
                />
                <span className="text-foreground">{line}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* What MIOS needs — the gates, framed as have/still-needs */}
      <div className="mt-4 border-t border-border pt-4">
        <SectionLabel>
          {status === "QUALIFIED" ? "Conditions Met" : "What MIOS Needs"}
        </SectionLabel>
        <ul className="space-y-2">
          {qualification.gates.map((gate) => (
            <NeedRow key={gate.name} gate={gate} />
          ))}
        </ul>
      </div>
    </Card>
  );
}
