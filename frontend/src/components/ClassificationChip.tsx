import { labelize } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Classification } from "@/types/dashboard";

// A colored chip for a strike's classification, shared by the Participation
// Radar, Strike Evolution, and elsewhere. Bullish positioning (call buying /
// put writing) reads green; bearish (call writing / put buying) reads red.
// Presentation only — the classification comes straight from the engine.

const STYLE: Record<Classification, string> = {
  long_buildup: "bg-bullish/15 text-bullish",
  short_covering: "bg-bullish/15 text-bullish",
  short_buildup: "bg-bearish/15 text-bearish",
  long_unwinding: "bg-bearish/15 text-bearish",
};

export function ClassificationChip({
  classification,
  className,
}: {
  classification: Classification | null;
  className?: string;
}) {
  if (!classification) {
    return <span className={cn("text-xs text-muted", className)}>—</span>;
  }
  return (
    <span
      className={cn(
        "inline-block whitespace-nowrap rounded px-1.5 py-0.5 text-xs font-medium",
        STYLE[classification],
        className,
      )}
    >
      {labelize(classification)}
    </span>
  );
}
