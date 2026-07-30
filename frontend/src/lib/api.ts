import type { DashboardResponse } from "@/types/dashboard";

/** The single endpoint this frontend consumes. */
export const DASHBOARD_URL = "/api/v1/dashboard";

/** Fetch the dashboard snapshot. Throws on non-2xx so TanStack Query retries. */
export async function fetchDashboard(
  signal?: AbortSignal,
): Promise<DashboardResponse> {
  const response = await fetch(DASHBOARD_URL, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Dashboard request failed: ${response.status}`);
  }
  return (await response.json()) as DashboardResponse;
}
