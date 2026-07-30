import type { OptionType } from "@/types/dashboard";

/** Stable DOM id for an option-chain row, used to scroll candidates into view. */
export function rowDomId(strike: string, optionType: OptionType): string {
  return `oc-${strike}-${optionType}`;
}
