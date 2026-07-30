import { useCallback, useState } from "react";

import { EngineStatus } from "@/components/EngineStatus";
import { EvidenceCard } from "@/components/EvidenceCard";
import { MarketContextCard } from "@/components/MarketContextCard";
import { OptionChain } from "@/components/OptionChain";
import { RecommendationCard } from "@/components/RecommendationCard";
import { TopCandidates } from "@/components/TopCandidates";
import { deriveAction, primaryPick } from "@/lib/decision";
import type { DashboardResponse } from "@/types/dashboard";

export function Dashboard({ data }: { data: DashboardResponse }) {
  const [highlightedRowId, setHighlightedRowId] = useState<string | null>(null);

  const selectRow = useCallback((rowId: string) => {
    setHighlightedRowId(rowId);
    const el = document.getElementById(rowId);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  const action = deriveAction(data);
  const pick = primaryPick(data.recommendation);

  return (
    <div id="top" className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecommendationCard action={action} recommendation={data.recommendation} />
        </div>
        <MarketContextCard context={data.context} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <EvidenceCard pick={pick} noTrade={data.no_trade} />
        </div>
        <TopCandidates candidates={data.top_candidates} onSelect={selectRow} />
      </div>

      <OptionChain rows={data.option_chain} highlightedRowId={highlightedRowId} />

      <EngineStatus engine={data.engine} />
    </div>
  );
}
