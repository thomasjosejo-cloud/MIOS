import { useState } from "react";

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
  // Set by Participation Radar; consumed by Strike Evolution and the Option
  // Chain highlight — so the dashboard behaves as one connected workspace.
  const [selected, setSelected] = useState<SelectedStrike | null>(null);

  return (
    <div id="top" className="space-y-4">
      {/* The market as a plain-language story, at the very top. */}
      <MarketNarrativeBanner narrative={data.narrative} />

      {/* Intelligence + decision row: where to look, and what MIOS recommends. */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <ParticipationRadar
            rows={data.participation}
            selected={selected}
            onSelect={setSelected}
          />
          <RecommendedTradeCard qualification={data.qualification} />
        </div>
        <div className="space-y-4">
          <MarketDominanceCard dominance={data.dominance} />
          <MarketContextCard context={data.context} />
        </div>
      </div>

      {/* Evolution of the strike the trader selected above. */}
      <StrikeEvolution selected={selected} />

      {/* Permanent market-intelligence card. */}
      <WhatIsHappeningCard narrative={data.narrative} />

      {/* Trimmed to 5 CE + 5 PE around ATM; qualified/watching/best marked, and
          the strike selected in Participation Radar is highlighted here too. */}
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
