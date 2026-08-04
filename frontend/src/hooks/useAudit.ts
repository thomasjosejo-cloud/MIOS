import { useQuery } from "@tanstack/react-query";

import { fetchAudit } from "@/lib/api";
import { POLL_INTERVAL_MS } from "@/hooks/useDashboard";
import type { AuditReport } from "@/types/dashboard";

/**
 * Fetch the decision-trace audit for the "Show your work" view.
 *
 * `enabled` is driven by whether the view is open: the audit is a debug/explain
 * view, so it costs nothing while collapsed, but stays in sync with the live
 * 2s dashboard poll while the trader has it open.
 */
export function useAudit(open: boolean) {
  return useQuery<AuditReport>({
    queryKey: ["audit"],
    queryFn: ({ signal }) => fetchAudit(signal),
    enabled: open,
    refetchInterval: open ? POLL_INTERVAL_MS : false,
    refetchIntervalInBackground: false,
    staleTime: 0,
    placeholderData: (previous) => previous,
  });
}
