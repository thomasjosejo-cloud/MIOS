import { useQuery } from "@tanstack/react-query";

import { fetchDashboard } from "@/lib/api";
import type { DashboardResponse } from "@/types/dashboard";

/** Poll interval in milliseconds (Sprint 7 spec: every 2 seconds). */
export const POLL_INTERVAL_MS = 2000;

export const DASHBOARD_QUERY_KEY = ["dashboard"] as const;

/**
 * Poll `GET /api/v1/dashboard` every 2s. Keeps the last successful snapshot on
 * screen across refetches and errors, and retries automatically on failure.
 */
export function useDashboard() {
  return useQuery<DashboardResponse>({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: ({ signal }) => fetchDashboard(signal),
    refetchInterval: POLL_INTERVAL_MS,
    refetchIntervalInBackground: true,
    retry: true,
    retryDelay: POLL_INTERVAL_MS,
    staleTime: 0,
    placeholderData: (previous) => previous,
  });
}
