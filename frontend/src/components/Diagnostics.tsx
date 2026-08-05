import { useState } from "react";
import { ChevronRight } from "lucide-react";

import { Card } from "@/components/ui/card";
import { CONNECTION_META, toneClass } from "@/lib/connection";
import { formatClock } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
  ConnectionState,
  EngineStatus as EngineStatusType,
  MarketSection,
} from "@/types/dashboard";

// A compact, collapsed diagnostics row that sits beside the Decision Trace at
// the bottom of the page — the operational detail EngineStatus used to show
// (health, runtime, data age) plus the last poll time and the connection state,
// tucked away rather than given a full section.

function Row({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="flex items-center justify-between py-1 text-xs">
      <span className="text-muted">{label}</span>
      <span className={cn("font-medium tabular-nums", tone ?? "text-foreground")}>
        {value}
      </span>
    </div>
  );
}

export function Diagnostics({
  engine,
  connection,
  market,
}: {
  engine: EngineStatusType;
  connection: ConnectionState;
  market: MarketSection;
}) {
  const [open, setOpen] = useState(false);
  const conn = CONNECTION_META[connection];

  const runtime =
    engine.pipeline_runtime_ms === null
      ? "—"
      : `${engine.pipeline_runtime_ms.toFixed(1)} ms`;
  const age =
    engine.data_age_seconds === null
      ? "—"
      : `${engine.data_age_seconds.toFixed(1)} s`;

  return (
    <Card id="diagnostics" className="scroll-mt-16 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-border/30"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2">
          <ChevronRight
            className={cn(
              "h-4 w-4 text-muted transition-transform",
              open && "rotate-90",
            )}
            aria-hidden
          />
          <span className="text-sm font-semibold">Diagnostics</span>
        </span>
        <span className="flex items-center gap-1.5 text-xs">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              engine.healthy ? "bg-bullish" : "bg-bearish",
            )}
            aria-hidden
          />
          <span className={engine.healthy ? "text-bullish" : "text-bearish"}>
            {engine.healthy ? "Healthy" : "Unavailable"}
          </span>
        </span>
      </button>

      {open && (
        <div className="divide-y divide-border px-4 pb-3">
          <Row label="Connection" value={conn.label} tone={toneClass(conn.tone)} />
          <Row label="Last poll" value={formatClock(market.updated_at)} />
          <Row
            label="Engine"
            value={engine.healthy ? "Healthy" : "Unavailable"}
            tone={engine.healthy ? "text-bullish" : "text-bearish"}
          />
          <Row label="Pipeline runtime" value={runtime} />
          <Row label="Data age" value={age} />
        </div>
      )}
    </Card>
  );
}
