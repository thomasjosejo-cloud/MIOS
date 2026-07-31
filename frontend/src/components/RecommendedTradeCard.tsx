import { Check, Eye, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
  BestCandidate,
  ConfidenceBand,
  QualificationGate,
  TradeQualification,
} from "@/types/dashboard";

// The decision centrepiece. When a trade qualifies it shows the RECOMMENDED
// TRADE (strike, confidence, evidence). When it does not it shows the trade
// status with the failed gates. In both cases the four gates and the best
// candidate MIOS is watching are shown. Every value comes from the API — the
// evidence list is rendered verbatim and never invented here.

const BAND_TONE: Record<ConfidenceBand, string> = {
  "Very High": "text-bullish",
  High: "text-bullish",
  Medium: "text-accent",
  Low: "text-bearish",
  "Very Low": "text-bearish",
};

function ConfidenceMeter({
  confidence,
  band,
}: {
  confidence: number;
  band: ConfidenceBand;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-xs uppercase tracking-wider text-muted">
          Confidence
        </span>
        <span className={cn("text-sm font-semibold", BAND_TONE[band])}>
          {band}
        </span>
      </div>
      <div className="mt-1 flex items-center gap-2">
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-border">
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
        <span className="w-12 text-right text-lg font-bold tabular-nums">
          {confidence}%
        </span>
      </div>
    </div>
  );
}

function GateRow({ gate }: { gate: QualificationGate }) {
  return (
    <li className="flex items-start gap-2 text-sm">
      {gate.passed ? (
        <Check className="mt-0.5 h-4 w-4 shrink-0 text-bullish" aria-hidden />
      ) : (
        <X className="mt-0.5 h-4 w-4 shrink-0 text-bearish" aria-hidden />
      )}
      <span className="flex-1">
        <span className="font-medium text-foreground">{gate.name}</span>
        {gate.mandatory && !gate.passed && (
          <span className="ml-1 text-xs text-bearish">(required)</span>
        )}
        <span className="block text-xs text-muted">{gate.reason}</span>
      </span>
    </li>
  );
}

function BestCandidatePanel({ candidate }: { candidate: BestCandidate }) {
  return (
    <div className="rounded-md border border-border bg-background/50 p-3">
      <div className="mb-1 flex items-center gap-1.5 text-xs uppercase tracking-wider text-muted">
        <Eye className="h-3.5 w-3.5" aria-hidden />
        Best Candidate
      </div>
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span className="text-xl font-bold tabular-nums">
            {candidate.strike}
          </span>
          <Badge variant={candidate.option_type === "CE" ? "bullish" : "bearish"}>
            {candidate.option_type}
          </Badge>
          <span className="text-sm text-muted">
            {labelize(candidate.classification)}
          </span>
        </span>
        <span className="text-sm font-semibold tabular-nums text-muted">
          {candidate.qualification}%
        </span>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted">{candidate.reason}</p>
    </div>
  );
}

export function RecommendedTradeCard({
  qualification,
}: {
  qualification: TradeQualification | null;
}) {
  if (!qualification) {
    return (
      <Card id="qualification" className="scroll-mt-16 border-2 p-5">
        <span className="text-xs font-semibold uppercase tracking-widest text-muted">
          Trade Status
        </span>
        <p className="mt-3 text-sm text-muted">Awaiting engine data…</p>
      </Card>
    );
  }

  const { qualified } = qualification;

  return (
    <Card
      id="qualification"
      className={cn(
        "scroll-mt-16 border-2 p-5",
        qualified ? "border-bullish/50 bg-bullish/5" : "border-border bg-card",
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-widest text-muted">
          {qualified ? "Recommended Trade" : "Trade Status"}
        </span>
        <span
          className={cn(
            "rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide",
            qualified
              ? "bg-bullish/15 text-bullish"
              : "bg-bearish/15 text-bearish",
          )}
        >
          {qualified ? "Trade Qualified" : "Not Qualified"}
        </span>
      </div>

      {qualified && qualification.strike ? (
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-4xl font-extrabold tabular-nums text-foreground">
            {qualification.strike}
          </span>
          {qualification.option_type && (
            <Badge
              variant={qualification.option_type === "CE" ? "bullish" : "bearish"}
            >
              {qualification.option_type}
            </Badge>
          )}
          {qualification.classification && (
            <span className="text-sm text-muted">
              {labelize(qualification.classification)}
            </span>
          )}
        </div>
      ) : (
        <p className="mt-3 text-sm text-muted">
          MIOS is standing aside — the required gates below have not all passed.
        </p>
      )}

      <div className="mt-4">
        <ConfidenceMeter
          confidence={qualification.confidence}
          band={qualification.band}
        />
      </div>

      {/* The four gates, always visible so the decision is explainable. */}
      <div className="mt-4 border-t border-border pt-4">
        <div className="mb-2 text-xs uppercase tracking-wider text-muted">
          Qualification Gates
        </div>
        <ul className="space-y-2">
          {qualification.gates.map((gate) => (
            <GateRow key={gate.name} gate={gate} />
          ))}
        </ul>
      </div>

      {/* Evidence — only shown when the engine provided it (never invented). */}
      {qualified && qualification.reasons.length > 0 && (
        <div className="mt-4 border-t border-border pt-4">
          <div className="mb-2 text-xs uppercase tracking-wider text-muted">
            Evidence
          </div>
          <ul className="space-y-1.5">
            {qualification.reasons.map((line, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Check
                  className="mt-0.5 h-4 w-4 shrink-0 text-bullish"
                  aria-hidden
                />
                <span className="text-foreground">{line}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Best candidate is always shown when present, even during NO TRADE. */}
      {qualification.best_candidate && (
        <div className="mt-4">
          <BestCandidatePanel candidate={qualification.best_candidate} />
        </div>
      )}
    </Card>
  );
}
