import { useState } from "react";
import { ChevronRight, TriangleAlert } from "lucide-react";

import { ClassificationChip } from "@/components/ClassificationChip";
import { Card } from "@/components/ui/card";
import { useAudit } from "@/hooks/useAudit";
import { formatInt, formatPercent, labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { AuditReport, Sentiment } from "@/types/dashboard";

// "Show your work" — the decision trace. Every dashboard conclusion (bias,
// regime, dominance, qualification, narrative) shown next to the raw per-strike
// evidence it was derived from. Backed entirely by GET /market/audit; the
// frontend only renders. Collapsed by default (it is an explain/debug view).

function sentimentTone(s: Sentiment | null): string {
  if (s === "bullish") return "text-bullish";
  if (s === "bearish") return "text-bearish";
  return "text-muted";
}

function Conclusion({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col">
      <span className="text-[11px] uppercase tracking-wider text-muted">{label}</span>
      <span className="mt-0.5 text-sm font-medium">{children}</span>
    </div>
  );
}

function Body({ audit }: { audit: AuditReport }) {
  const bias = audit.bias;
  return (
    <div className="space-y-4 px-4 pb-4">
      {/* Consistency contradictions — the whole point of the trace: never hide them. */}
      {audit.consistency_warnings.length > 0 ? (
        <div className="rounded-md border-l-2 border-bearish bg-bearish/10 p-3">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-bearish">
            <TriangleAlert className="h-3.5 w-3.5" aria-hidden />
            Consistency warnings ({audit.consistency_warnings.length})
          </div>
          <ul className="mt-1 space-y-1">
            {audit.consistency_warnings.map((w, i) => (
              <li key={i} className="text-sm text-foreground">
                {w}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-xs text-bullish">
          ✓ No contradictions — every conclusion agrees with the others.
        </p>
      )}

      {/* Conclusions */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <Conclusion label="Spot / ATM">
          {audit.spot ?? "—"} / {audit.atm ?? "—"}
        </Conclusion>
        <Conclusion label="Control">
          {bias ? labelize(bias.controlling_side).toUpperCase() : "—"}
        </Conclusion>
        <Conclusion label="Regime">
          {audit.structure_pattern ? labelize(audit.structure_pattern) : "—"}
          {audit.structure_trend ? ` · ${labelize(audit.structure_trend)}` : ""}
        </Conclusion>
        <Conclusion label="Momentum">
          {audit.momentum ? labelize(audit.momentum) : "—"}
        </Conclusion>
        <Conclusion label="Decision">
          {audit.qualification
            ? `${audit.qualification.decision} · ${audit.qualification.confidence}%`
            : "—"}
        </Conclusion>
        <Conclusion label="Narrative">
          {audit.narrative ? labelize(audit.narrative.tone) : "—"}
        </Conclusion>
      </div>

      {/* Bias scores + the engine's own evidence lines */}
      {bias && (
        <div className="rounded-md border border-border bg-background/40 p-3">
          <div className="text-[11px] uppercase tracking-wider text-muted">
            Bias score
          </div>
          <div className="mt-1 text-sm">
            <span className="text-bullish">bull {formatInt(Math.round(bias.bull_score))}</span>
            {"  vs  "}
            <span className="text-bearish">bear {formatInt(Math.round(bias.bear_score))}</span>
            {"  →  net "}
            <span className={bias.net_score >= 0 ? "text-bullish" : "text-bearish"}>
              {bias.net_score >= 0 ? "+" : ""}
              {formatInt(Math.round(bias.net_score))}
            </span>
          </div>
          <ul className="mt-2 space-y-0.5">
            {bias.evidence.map((line, i) => (
              <li key={i} className="text-xs text-muted">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Raw per-strike evidence the conclusions were derived from */}
      <div>
        <div className="mb-1 text-[11px] uppercase tracking-wider text-muted">
          Per-strike evidence (±ATM)
        </div>
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-card">
              <tr className="border-b border-border text-left text-[11px] uppercase tracking-wider text-muted">
                <th className="px-2.5 py-2 font-medium">Strike</th>
                <th className="px-2.5 py-2 text-right font-medium">OI Δ</th>
                <th className="px-2.5 py-2 text-right font-medium">OI %</th>
                <th className="px-2.5 py-2 text-right font-medium">Prem %</th>
                <th className="px-2.5 py-2 text-right font-medium">Vol %</th>
                <th className="px-2.5 py-2 font-medium">Classification</th>
                <th className="px-2.5 py-2 font-medium">Meaning</th>
                <th className="px-2.5 py-2 text-right font-medium">Signed score</th>
              </tr>
            </thead>
            <tbody>
              {audit.strikes.map((r) => (
                <tr
                  key={`${r.strike}-${r.option_type}`}
                  className="border-b border-border/60 tabular-nums last:border-0"
                >
                  <td className="whitespace-nowrap px-2.5 py-1.5">
                    <span className="font-semibold">{r.strike}</span>{" "}
                    <span className={r.option_type === "CE" ? "text-bullish" : "text-bearish"}>
                      {r.option_type}
                    </span>
                  </td>
                  <td className="px-2.5 py-1.5 text-right text-muted">
                    {formatInt(r.oi_change)}
                  </td>
                  <td className="px-2.5 py-1.5 text-right">{formatPercent(r.oi_change_pct)}</td>
                  <td className="px-2.5 py-1.5 text-right">{formatPercent(r.premium_change_pct)}</td>
                  <td className="px-2.5 py-1.5 text-right">{formatPercent(r.volume_change_pct)}</td>
                  <td className="px-2.5 py-1.5">
                    <ClassificationChip classification={r.classification} />
                  </td>
                  <td className={cn("px-2.5 py-1.5", sentimentTone(r.sentiment))}>
                    {r.sentiment ? labelize(r.sentiment) : "—"}
                  </td>
                  <td className={cn("px-2.5 py-1.5 text-right", sentimentTone(r.sentiment))}>
                    {r.signed_score >= 0 ? "+" : ""}
                    {formatInt(r.signed_score)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function AuditPanel() {
  const [open, setOpen] = useState(false);
  const { data, isLoading, isError } = useAudit(open);

  return (
    <Card id="decision-trace" className="scroll-mt-16 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-border/30"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2">
          <ChevronRight
            className={cn("h-4 w-4 text-muted transition-transform", open && "rotate-90")}
            aria-hidden
          />
          <span className="text-sm font-semibold">Decision Trace</span>
          <span className="text-xs text-muted">— show your work</span>
        </span>
        <span className="text-xs text-muted">
          {open ? "hide" : "every conclusion, traced to raw evidence"}
        </span>
      </button>

      {open &&
        (isLoading && !data ? (
          <p className="px-4 pb-4 text-sm text-muted">Loading decision trace…</p>
        ) : isError ? (
          <p className="px-4 pb-4 text-sm text-muted">
            Decision trace unavailable (engine has not produced a snapshot yet).
          </p>
        ) : data ? (
          <Body audit={data} />
        ) : null)}
    </Card>
  );
}
