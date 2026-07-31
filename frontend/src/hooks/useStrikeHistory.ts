import { useQuery } from "@tanstack/react-query";

import { fetchStrikeHistory } from "@/lib/api";
import type { OptionType, StrikeHistory } from "@/types/dashboard";
import { POLL_INTERVAL_MS } from "@/hooks/useDashboard";

/**
 * Fetch the selected strike's historical progression for Strike Evolution.
 * Disabled until a strike is selected; polls so the series stays current.
 */
export function useStrikeHistory(
  selected: { strike: string; option_type: OptionType } | null,
) {
  return useQuery<StrikeHistory>({
    queryKey: ["strike-history", selected?.strike, selected?.option_type],
    queryFn: ({ signal }) =>
      fetchStrikeHistory(selected!.strike, selected!.option_type, signal),
    enabled: selected !== null,
    refetchInterval: POLL_INTERVAL_MS,
    refetchIntervalInBackground: true,
    staleTime: 0,
    placeholderData: (previous) => previous,
  });
}
