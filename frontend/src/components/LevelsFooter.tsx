import { formatDecimal } from "@/lib/format";
import type { MarketContext } from "@/types/dashboard";

// Section 10: the footer — the immediate support and resistance levels from the
// structure engine. These are price levels, not a directional call, so they are
// rendered neutral (no green/red) — colour is reserved for genuine bull/bear
// state elsewhere.

function Level({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="flex flex-col">
      <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">
        {label}
      </span>
      <span className="text-base font-semibold tabular-nums text-foreground">
        {value === null ? "—" : formatDecimal(value, 0)}
      </span>
    </div>
  );
}

export function LevelsFooter({ context }: { context: MarketContext | null }) {
  return (
    <footer
      id="levels"
      className="flex items-center justify-between rounded-xl border-[0.5px] border-border bg-card px-4 py-3"
    >
      <Level label="Immediate support" value={context?.immediate_support ?? null} />
      <span className="h-8 w-px bg-border" aria-hidden />
      <Level
        label="Immediate resistance"
        value={context?.immediate_resistance ?? null}
      />
    </footer>
  );
}
