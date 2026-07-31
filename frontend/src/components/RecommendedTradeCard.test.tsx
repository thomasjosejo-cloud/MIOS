import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RecommendedTradeCard } from "@/components/RecommendedTradeCard";
import { dashboardFixture, noTradeFixture } from "@/test/fixtures";

describe("RecommendedTradeCard", () => {
  it("shows the qualified trade with strike, confidence and evidence", () => {
    render(
      <RecommendedTradeCard qualification={dashboardFixture.qualification} />,
    );

    expect(screen.getByText("Recommended Trade")).toBeInTheDocument();
    expect(screen.getByText("Trade Qualified")).toBeInTheDocument();
    // 25150 appears both as the qualified strike and the best candidate.
    expect(screen.getAllByText("25150").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("Very High")).toBeInTheDocument();
    // Evidence is rendered verbatim from the API.
    expect(screen.getByText("Unusual activity flagged")).toBeInTheDocument();
  });

  it("shows all four gates as passed for a qualified trade", () => {
    render(
      <RecommendedTradeCard qualification={dashboardFixture.qualification} />,
    );

    for (const gate of [
      "Market Regime",
      "Options Participation",
      "CE vs PE Control",
      "Strike Quality",
    ]) {
      expect(screen.getByText(gate)).toBeInTheDocument();
    }
  });

  it("shows NOT QUALIFIED with the failed gate and best candidate on no-trade", () => {
    render(<RecommendedTradeCard qualification={noTradeFixture.qualification} />);

    expect(screen.getByText("Trade Status")).toBeInTheDocument();
    expect(screen.getByText("Not Qualified")).toBeInTheDocument();
    // The failed mandatory gate reason is shown.
    expect(
      screen.getByText("No trend or breakout; market is sideways/choppy."),
    ).toBeInTheDocument();
    expect(screen.getByText("(required)")).toBeInTheDocument();
    // The best candidate MIOS is watching is still shown during no-trade.
    expect(screen.getByText("Best Candidate")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Good option activity, but market structure has not confirmed yet.",
      ),
    ).toBeInTheDocument();
  });

  it("renders an awaiting message when there is no qualification", () => {
    render(<RecommendedTradeCard qualification={null} />);

    expect(screen.getByText("Awaiting engine data…")).toBeInTheDocument();
  });
});
