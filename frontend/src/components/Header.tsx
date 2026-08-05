import { cn } from "@/lib/utils";
import { CONNECTION_META, toneClass, toneDotClass } from "@/lib/connection";
import type { ConnectionState, MarketSection } from "@/types/dashboard";

// Section 1: the page's only chrome — wordmark, Fyers connection status, and
// the market open/closed state. No navigation (single-page app), no price (the
// price row is its own section in the page body).
export function Header({
  market,
  connection,
}: {
  market: MarketSection;
  connection: ConnectionState;
}) {
  const isLive = market.status === "LIVE";
  const conn = CONNECTION_META[connection];

  return (
    <header className="sticky top-0 z-20 border-b-[0.5px] border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-2xl items-center justify-between px-3">
        <span className="text-sm font-bold tracking-wide text-foreground">MIOS</span>

        <div className="flex items-center gap-4 text-xs font-medium">
          <span className="flex items-center gap-1.5" title="Fyers connection">
            <span
              className={cn("h-2 w-2 rounded-full", toneDotClass(conn.tone))}
              aria-hidden
            />
            <span className={toneClass(conn.tone)}>{conn.label}</span>
          </span>
          <span className="flex items-center gap-1.5" title="Market session">
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
          </span>
        </div>
      </div>
    </header>
  );
}
