import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  type Action,
  primaryPick,
  secondaryPick,
} from "@/lib/decision";
import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { RecommendationReport, StrikeRecommendation } from "@/types/dashboard";

const ACTION_STYLES: Record<Action, { label: string; frame: string; text: string }> = {
  BUY: {
    label: "BUY",
    frame: "border-bullish/50 bg-bullish/10",
    text: "text-bullish",
  },
  NO_TRADE: {
    label: "NO TRADE",
    frame: "border-bearish/50 bg-bearish/10",
    text: "text-bearish",
  },
  WAITING: {
    label: "WAITING",
    frame: "border-border bg-card",
    text: "text-muted",
  },
};

function SideLine({
  pick,
  primary,
}: {
  pick: StrikeRecommendation;
  primary?: boolean;
}) {
  return (
    <div className="flex items-baseline gap-2">
      <span
        className={cn(
          "font-bold tabular-nums",
          primary ? "text-4xl" : "text-xl text-muted",
        )}
      >
        {pick.strike}
      </span>
      <Badge variant={pick.option_type === "CE" ? "bullish" : "bearish"}>
        {pick.option_type}
      </Badge>
      <span className={cn("text-sm", primary ? "text-foreground" : "text-muted")}>
        {labelize(pick.classification)}
      </span>
    </div>
  );
}

export function RecommendationCard({
  action,
  recommendation,
}: {
  action: Action;
  recommendation: RecommendationReport | null;
}) {
  const style = ACTION_STYLES[action];
  const primary = primaryPick(recommendation);
  const secondary = secondaryPick(recommendation);

  return (
    <Card
      id="recommendation"
      className={cn("scroll-mt-16 border-2 p-5", style.frame)}
    >
      <div className="flex items-center justify-between">
        <span
          className={cn(
            "text-xs font-semibold uppercase tracking-widest text-muted",
          )}
        >
          Recommendation
        </span>
        {action === "BUY" && <ArrowUpRight className={cn("h-5 w-5", style.text)} />}
      </div>

      <div
        className={cn("mt-1 text-3xl font-extrabold tracking-tight", style.text)}
      >
        {style.label}
      </div>

      {action === "BUY" && primary ? (
        <div className="mt-4 space-y-3">
          <SideLine pick={primary} primary />
          <p className="text-sm leading-relaxed text-muted">{primary.reason}</p>
          {secondary && (
            <div className="border-t border-border pt-3">
              <div className="mb-1 text-xs uppercase tracking-wider text-muted">
                Also
              </div>
              <SideLine pick={secondary} />
            </div>
          )}
        </div>
      ) : action === "NO_TRADE" ? (
        <p className="mt-3 text-sm text-muted">
          No strike meets the engine's conviction threshold right now.
        </p>
      ) : (
        <p className="mt-3 text-sm text-muted">Awaiting engine data…</p>
      )}
    </Card>
  );
}
