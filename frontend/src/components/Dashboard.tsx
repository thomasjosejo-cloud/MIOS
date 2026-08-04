import { useCallback, useState } from "react";

import { EngineStatus } from "@/components/EngineStatus";
import { MarketContextCard } from "@/components/MarketContextCard";
import { MarketDominanceCard } from "@/components/MarketDominanceCard";
import { MarketNarrativeBanner } from "@/components/MarketNarrativeBanner";
import {
  ParticipationRadar,
  type SelectedStrike,
} from "@/components/ParticipationRadar";
import { ParticipationStatus } from "@/components/ParticipationStatus";
import { RecommendedTradeCard } from "@/components/RecommendedTradeCard";
import { StrikeEvolution } from "@/components/StrikeEvolution";
import { WhatIsHappeningCard } from "@/components/WhatIsHappeningCard";
import type { DashboardResponse } from "@/types/dashboard";

export function Dashboard({ data }: { data: DashboardResponse }) {
  // The one piece of shared UI state: which strike the trader is inspecting.
  // Set by Participation Radar; consumed by Strike Evolution and the Recommended
  // Trade "inspecting" chip — so the dashboard behaves as one connected
  // workspace.
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

  // Market Control for the Participation Status card — the canonical
  // controlling side, from the context (falling back to dominance).
  const marketControl =
    data.context?.controlling_side ?? data.dominance?.control ?? null;

  return (
    <div id="top" className="space-y-4">
      {/* The decision flow, top to bottom:
          Narrative → Radar → Recommended Trade → Participation Status →
          Strike Evolution → Market Context. */}
      <MarketNarrativeBanner narrative={data.narrative} />

      <ParticipationRadar
        rows={data.participation}
        atmStrike={data.market.atm_strike}
        selected={selected}
        onSelect={selectStrike}
      />

      <RecommendedTradeCard
        qualification={data.qualification}
        inspecting={selected}
      />

      <ParticipationStatus
        qualification={data.qualification}
        participation={data.participation}
        control={marketControl}
      />

      <StrikeEvolution selected={selected} />

      {/* Market Context — the supporting cards, unchanged internally. */}
      <div className="grid gap-4 lg:grid-cols-3">
        <MarketDominanceCard dominance={data.dominance} />
        <MarketContextCard context={data.context} />
        <WhatIsHappeningCard narrative={data.narrative} />
      </div>

      <EngineStatus engine={data.engine} />
    </div>
  );
}
