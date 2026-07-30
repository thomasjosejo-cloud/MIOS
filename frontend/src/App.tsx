import { Dashboard } from "@/components/Dashboard";
import { DashboardSkeleton } from "@/components/DashboardSkeleton";
import { ErrorState } from "@/components/ErrorState";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { useDashboard } from "@/hooks/useDashboard";
import type { MarketSection } from "@/types/dashboard";

const CLOSED_MARKET: MarketSection = {
  spot: null,
  change: null,
  change_percent: null,
  status: "CLOSED",
  updated_at: null,
};

export default function App() {
  const { data, failureCount } = useDashboard();

  // Keep the last snapshot on screen across failed polls; only fall back to the
  // error state when a failure occurs before any data has ever loaded. TanStack
  // Query keeps retrying underneath either way.
  const content = data ? (
    <Dashboard data={data} />
  ) : failureCount > 0 ? (
    <ErrorState />
  ) : (
    <DashboardSkeleton />
  );

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header market={data?.market ?? CLOSED_MARKET} />
        <main className="flex-1 overflow-y-auto p-4">{content}</main>
      </div>
    </div>
  );
}
