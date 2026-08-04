import type { ReactNode } from "react";

import { ConnectionGate } from "@/components/ConnectionGate";
import { Dashboard } from "@/components/Dashboard";
import { DashboardSkeleton } from "@/components/DashboardSkeleton";
import { ErrorState } from "@/components/ErrorState";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { useDashboard } from "@/hooks/useDashboard";
import type { MarketSection } from "@/types/dashboard";

const CLOSED_MARKET: MarketSection = {
  spot: null,
  atm_strike: null,
  change: null,
  change_percent: null,
  status: "CLOSED",
  updated_at: null,
};

export default function App() {
  const { data, failureCount } = useDashboard();

  // Routing:
  //  - no data yet   -> skeleton (or error after a failed first load)
  //  - connected     -> the live dashboard
  //  - anything else -> the connection gate (Connect button / status)
  // TanStack Query keeps polling every 2s, so the view flips automatically the
  // moment the backend connection state changes — no manual refresh or restart.
  let content: ReactNode;
  if (!data) {
    content = failureCount > 0 ? <ErrorState /> : <DashboardSkeleton />;
  } else if (data.connection_state === "connected") {
    content = <Dashboard data={data} />;
  } else {
    content = <ConnectionGate state={data.connection_state} />;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          market={data?.market ?? CLOSED_MARKET}
          connection={data?.connection_state ?? "not_connected"}
        />
        <main className="flex-1 overflow-y-auto p-4">{content}</main>
      </div>
    </div>
  );
}
