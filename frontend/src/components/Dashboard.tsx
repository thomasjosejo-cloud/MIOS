import { useCallback, useState } from "react";

import { EngineStatus } from "@/components/EngineStatus";
import { MarketContextCard } from "@/components/MarketContextCard";
import { MarketDominanceCard } from "@/components/MarketDominanceCard";
import { MarketNarrativeBanner } from "@/components/MarketNarrativeBanner";
import { OptionChain } from "@/components/OptionChain";
import {
  ParticipationRadar,
  type SelectedStrike,
} from "@/components/ParticipationRadar";
import { RecommendedTradeCard } from "@/components/RecommendedTradeCard";
import { StrikeEvolution } from "@/components/StrikeEvolution";
import { WhatIsHappeningCard } from "@/components/WhatIsHappeningCard";
import type { DashboardResponse } from "@/types/dashboard";

export function Dashboard({ data }: { data: DashboardResponse }) {
  // The one piece of shared UI state: which strike the trader is inspecting.
  // Set by Participation Radar; consumed by Strike Evolution, the Recommended
  // Trade "inspecting" chip, and the Option Chain highlight — so the dashboard
  // behaves as one connected workspace.
  const [selected, setSelected] = useState<SelectedStrike | null>(null);

  const selectStrike = useCallback((s: SelectedStrike) => {
    setSelected(s);
    // Bring the evolution of the just-selected strike into view smoothly.
    requestAnimationFrame(() => {
      document
        .getElementById("strike-evolution")
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }, []);

  return (
    <div id="top" className="space-y-4">
      {/* 1. The market as a plain-language story, at the very top. */}
      <MarketNarrativeBanner narrative={data.narrative} />

      {/* 2 + 3. Main column: where to look, then what MIOS recommends.
          Right rail: the supporting market context, so the page stays wide
          rather than one long vertical stack. */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <ParticipationRadar
            rows={data.participation}
            selected={selected}
            onSelect={selectStrike}
          />
          <RecommendedTradeCard
            qualification={data.qualification}
            inspecting={selected}
          />
        </div>
        <div className="space-y-4">
          <MarketDominanceCard dominance={data.dominance} />
          <MarketContextCard context={data.context} />
          <WhatIsHappeningCard narrative={data.narrative} />
        </div>
      </div>

      {/* 4. Evolution of the strike selected above (full width for the series). */}
      <StrikeEvolution selected={selected} />

      {/* 5. The strike in the context of the whole chain; the inspected strike
          is strongly highlighted here too. */}
      <OptionChain
        rows={data.option_chain}
        highlightedRowId={null}
        qualification={data.qualification}
        selected={selected}
      />

      <EngineStatus engine={data.engine} />
    </div>
  );
}
