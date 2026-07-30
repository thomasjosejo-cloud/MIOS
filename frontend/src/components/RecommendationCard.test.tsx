import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RecommendationCard } from "@/components/RecommendationCard";
import { deriveAction } from "@/lib/decision";
import { dashboardFixture, noTradeFixture } from "@/test/fixtures";

describe("RecommendationCard", () => {
  it("renders a BUY with the best strike, type, and classification", () => {
    const action = deriveAction(dashboardFixture);
    render(
      <RecommendationCard
        action={action}
        recommendation={dashboardFixture.recommendation}
      />,
    );

    expect(screen.getByText("BUY")).toBeInTheDocument();
    expect(screen.getByText("25150")).toBeInTheDocument();
    expect(screen.getByText("CE")).toBeInTheDocument();
    expect(screen.getByText("Long Build-up")).toBeInTheDocument();
  });

  it("renders NO TRADE when the engine declares no trade", () => {
    const action = deriveAction(noTradeFixture);
    render(
      <RecommendationCard
        action={action}
        recommendation={noTradeFixture.recommendation}
      />,
    );

    expect(screen.getByText("NO TRADE")).toBeInTheDocument();
    expect(screen.queryByText("25150")).not.toBeInTheDocument();
  });
});
