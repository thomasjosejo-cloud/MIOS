import { cn } from "@/lib/utils";
import {
  formatClock,
  formatDecimal,
  formatPercent,
  formatSignedDecimal,
  signOf,
} from "@/lib/format";
import type { MarketSection } from "@/types/dashboard";

function directionClass(sign: -1 | 0 | 1): string {
  if (sign > 0) return "text-bullish";
  if (sign < 0) return "text-bearish";
  return "text-muted";
}

export function Header({ market }: { market: MarketSection }) {
  const isLive = market.status === "LIVE";
  const changeSign = signOf(market.change);

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur">
      <div className="flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-2 md:hidden">
          <span className="text-sm font-semibold tracking-wide">MIOS</span>
        </div>
        <div className="ml-auto flex items-center gap-2 text-xs font-medium">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              isLive ? "live-dot bg-bullish" : "bg-muted",
            )}
            aria-hidden
          />
          <span className={isLive ? "text-bullish" : "text-muted"}>
            {market.status}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-baseline gap-x-6 gap-y-1 px-4 pb-3">
        <span className="text-sm font-semibold text-muted">NIFTY</span>
        <span
          className={cn(
            "text-lg font-semibold tabular-nums",
            directionClass(changeSign),
          )}
        >
          {formatSignedDecimal(market.change)}
        </span>
        <span className="text-2xl font-bold tabular-nums text-foreground">
          {formatDecimal(market.spot)}
        </span>
        <span
          className={cn("text-sm font-medium tabular-nums", directionClass(changeSign))}
        >
          {formatPercent(market.change_percent)}
        </span>
        <span className="ml-auto text-xs text-muted">
          Updated {formatClock(market.updated_at)}
        </span>
      </div>
    </header>
  );
}
