import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MarketContextCard } from "@/components/MarketContextCard";
import { dashboardFixture } from "@/test/fixtures";
import type { MarketContext } from "@/types/dashboard";

const baseContext = dashboardFixture.context as MarketContext;

describe("MarketContextCard", () => {
  it("renders the full contradiction sentence as a callout when present", () => {
    const context: MarketContext = {
      ...baseContext,
      contradiction:
        "Options activity is bullish (put writing / call buying) but price structure shows a downtrend (LH-LL).",
    };
    render(<MarketContextCard context={context} />);

    // The full sentence is shown verbatim — not a flat "Yes".
    expect(
      screen.getByText(/price structure shows a downtrend/i),
    ).toBeInTheDocument();
    expect(screen.getByText("Contradiction")).toBeInTheDocument();
    expect(screen.queryByText("Yes")).not.toBeInTheDocument();
  });

  it("shows no contradiction callout when there is none", () => {
    const context: MarketContext = { ...baseContext, contradiction: null };
    render(<MarketContextCard context={context} />);

    expect(screen.queryByText("Contradiction")).not.toBeInTheDocument();
  });
});
