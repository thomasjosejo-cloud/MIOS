import type {
  DashboardResponse,
  OptionType,
  StrikeHistory,
} from "@/types/dashboard";

/** The dashboard snapshot endpoint this frontend polls. */
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

/**
 * Fetch a strike's historical progression for the Strike Evolution panel.
 * The backend owns the series; the frontend only renders whatever it returns.
 */
export async function fetchStrikeHistory(
  strike: string,
  optionType: OptionType,
  signal?: AbortSignal,
): Promise<StrikeHistory> {
  const params = new URLSearchParams({
    strike,
    option_type: optionType,
  });
  const response = await fetch(`/api/v1/market/strike-history?${params}`, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Strike history request failed: ${response.status}`);
  }
  return (await response.json()) as StrikeHistory;
}
