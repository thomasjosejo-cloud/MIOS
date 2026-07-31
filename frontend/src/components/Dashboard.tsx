import { EngineStatus } from "@/components/EngineStatus";
import { MarketContextCard } from "@/components/MarketContextCard";
import { MarketDominanceCard } from "@/components/MarketDominanceCard";
import { MarketNarrativeBanner } from "@/components/MarketNarrativeBanner";
import { OptionChain } from "@/components/OptionChain";
import { RecommendedTradeCard } from "@/components/RecommendedTradeCard";
import { WhatIsHappeningCard } from "@/components/WhatIsHappeningCard";
import type { DashboardResponse } from "@/types/dashboard";

export function Dashboard({ data }: { data: DashboardResponse }) {
  return (
    <div id="top" className="space-y-4">
      {/* The market as a plain-language story, at the very top. */}
      <MarketNarrativeBanner narrative={data.narrative} />

      <div className="grid gap-4 lg:grid-cols-3">
        {/* The decision: recommended trade or trade status + gates. */}
        <div className="lg:col-span-2">
          <RecommendedTradeCard qualification={data.qualification} />
        </div>
        <div className="space-y-4">
          <MarketDominanceCard dominance={data.dominance} />
          <MarketContextCard context={data.context} />
        </div>
      </div>

      {/* Permanent market-intelligence card. */}
      <WhatIsHappeningCard narrative={data.narrative} />

      {/* Trimmed to 5 CE + 5 PE around ATM; recommended strike highlighted. */}
      <OptionChain rows={data.option_chain} highlightedRowId={null} />

      <EngineStatus engine={data.engine} />
    </div>
  );
}
