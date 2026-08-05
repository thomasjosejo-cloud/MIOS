import { useCallback, useState } from "react";

import { AuditPanel } from "@/components/AuditPanel";
import { ContextChips } from "@/components/ContextChips";
import { ContextDisclosure } from "@/components/ContextDisclosure";
import { Diagnostics } from "@/components/Diagnostics";
import { LevelsFooter } from "@/components/LevelsFooter";
import { MarketDominanceCard } from "@/components/MarketDominanceCard";
import { MarketNarrativeBanner } from "@/components/MarketNarrativeBanner";
import {
  ParticipationRadar,
  type SelectedStrike,
} from "@/components/ParticipationRadar";
import { ParticipationStatus } from "@/components/ParticipationStatus";
import { PriceRow } from "@/components/PriceRow";
import { RecommendedTradeCard } from "@/components/RecommendedTradeCard";
import { StrikeEvolution } from "@/components/StrikeEvolution";
import type { DashboardResponse } from "@/types/dashboard";

export function Dashboard({ data }: { data: DashboardResponse }) {
  // The one piece of shared UI state: which strike the trader is inspecting.
  // Set by Participation Radar; consumed by Strike Evolution and the Recommended
  // Trade "inspecting" chip.
  const [selected, setSelected] = useState<SelectedStrike | null>(null);

  const selectStrike = useCallback((s: SelectedStrike) => {
    setSelected(s);
    requestAnimationFrame(() => {
      document
        .getElementById("strike-evolution")
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }, []);

  // Market Control for the Participation Status card — the canonical
  // controlling side, from context (falling back to dominance).
  const marketControl =
    data.context?.controlling_side ?? data.dominance?.control ?? null;

  return (
    // A single continuous, mobile-first column. Sections run top-to-bottom in a
    // fixed decision order — no navigation, no multi-page split.
    <div id="top" className="space-y-3">
      {/* 2. Price row: spot, change, change %, opening-gap badge. */}
      <PriceRow
        market={data.market}
        gapClassification={data.context?.gap_classification ?? null}
        gapPct={data.context?.gap_pct ?? null}
      />

      {/* 3. Narrative — tone-coloured background, headline — with the market
          context, contradiction and evidence folded in as a one-tap expand. */}
      <div className="space-y-2">
        <MarketNarrativeBanner narrative={data.narrative} />
        <ContextDisclosure context={data.context} />
      </div>

      {/* 4. Context chips: trend, pattern, recent swing (omitted if no swings). */}
      <ContextChips context={data.context} />

      {/* 5. Market control — buyers / writers split. */}
      <MarketDominanceCard dominance={data.dominance} />

      {/* 6. Participation radar — ATM±2, CE+PE merged per strike. */}
      <ParticipationRadar
        rows={data.participation}
        atmStrike={data.market.atm_strike}
        strikeStep={data.market.strike_step}
        selected={selected}
        onSelect={selectStrike}
      />

      {/* 7. Recommended trade — strike, side, status, confidence. */}
      <RecommendedTradeCard
        qualification={data.qualification}
        inspecting={selected}
      />

      {/* 8. Participation status for the recommended strike. */}
      <ParticipationStatus
        qualification={data.qualification}
        participation={data.participation}
        control={marketControl}
      />

      {/* 9. Strike evolution — % trend for the selected strike. */}
      <StrikeEvolution selected={selected} />

      {/* 10. Footer — immediate support / resistance. */}
      <LevelsFooter context={data.context} />

      {/* Bottom utility rows: the full decision trace and compact operational
          diagnostics, both collapsed by default. */}
      <AuditPanel />
      <Diagnostics
        engine={data.engine}
        connection={data.connection_state}
        market={data.market}
      />
    </div>
  );
}
