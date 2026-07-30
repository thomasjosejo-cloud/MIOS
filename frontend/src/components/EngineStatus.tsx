import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { EngineStatus as EngineStatusType } from "@/types/dashboard";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-muted">{label}</span>
      <span className="text-sm font-medium tabular-nums text-foreground">
        {value}
      </span>
    </div>
  );
}

export function EngineStatus({ engine }: { engine: EngineStatusType }) {
  const runtime =
    engine.pipeline_runtime_ms === null
      ? "—"
      : `${engine.pipeline_runtime_ms.toFixed(1)} ms`;
  const age =
    engine.data_age_seconds === null
      ? "—"
      : `${engine.data_age_seconds.toFixed(1)} s`;

  return (
    <Card id="engine-status" className="scroll-mt-16">
      <CardHeader>
        <CardTitle>Engine Status</CardTitle>
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
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-3">
          <Metric label="Healthy" value={engine.healthy ? "Yes" : "No"} />
          <Metric label="Runtime" value={runtime} />
          <Metric label="Data Age" value={age} />
        </div>
      </CardContent>
    </Card>
  );
}
