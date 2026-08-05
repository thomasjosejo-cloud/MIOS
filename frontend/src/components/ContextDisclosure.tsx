import { ChevronRight } from "lucide-react";

import { MarketContextCard } from "@/components/MarketContextCard";
import type { MarketContext } from "@/types/dashboard";

// Folds the market-context detail — including the contradiction callout and the
// evidence disclosure — inline under the Narrative card as a one-tap expand,
// rather than a standalone section. Reuses MarketContextCard unchanged; a
// contradiction is hinted on the trigger so it is discoverable while collapsed.
export function ContextDisclosure({
  context,
}: {
  context: MarketContext | null;
}) {
  return (
    <details id="context-detail" className="group scroll-mt-16">
      <summary className="flex cursor-pointer select-none items-center gap-1.5 px-1 py-1 text-xs text-muted transition-colors hover:text-foreground">
        <ChevronRight
          className="h-3.5 w-3.5 transition-transform group-open:rotate-90"
          aria-hidden
        />
        Market context &amp; evidence
        {context?.contradiction && (
          <span className="ml-1 font-semibold text-bearish">· contradiction</span>
        )}
      </summary>
      <div className="mt-2">
        <MarketContextCard context={context} />
      </div>
    </details>
  );
}
