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
    expect(screen.getByText("TRADE QUALIFIED")).toBeInTheDocument();
    expect(screen.getByText("25150")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
    // The qualitative band comes from the engine, uppercased for the badge.
    expect(screen.getByText("VERY HIGH")).toBeInTheDocument();
    // Evidence is rendered verbatim from the API.
    expect(screen.getByText("Unusual activity flagged")).toBeInTheDocument();
  });

  it("shows all four gates as met for a qualified trade", () => {
    render(
      <RecommendedTradeCard qualification={dashboardFixture.qualification} />,
    );

    expect(screen.getByText("Conditions Met")).toBeInTheDocument();
    for (const gate of [
      "Market Regime",
      "Options Participation",
      "CE vs PE Control",
      "Strike Quality",
    ]) {
      expect(screen.getByText(gate)).toBeInTheDocument();
    }
  });

  it("shows WATCHING with the watched strike and what MIOS needs on no-trade", () => {
    render(<RecommendedTradeCard qualification={noTradeFixture.qualification} />);

    // Not qualified but a candidate exists -> WATCHING, with the watched strike.
    expect(screen.getByText("WATCHING")).toBeInTheDocument();
    expect(screen.getByText("25150")).toBeInTheDocument();
    expect(screen.getByText("What MIOS Needs")).toBeInTheDocument();
    // The failing mandatory gate and its reason are shown.
    expect(
      screen.getByText("No trend or breakout; market is sideways/choppy."),
    ).toBeInTheDocument();
    expect(screen.getByText("required")).toBeInTheDocument();
  });

  it("shows NO TRADE with no strike when there is no candidate", () => {
    const base = noTradeFixture.qualification;
    if (!base) throw new Error("fixture missing qualification");
    const q = { ...base, best_candidate: null, reasons: [] };
    render(<RecommendedTradeCard qualification={q} />);

    expect(screen.getByText("NO TRADE")).toBeInTheDocument();
    expect(screen.getByText(/No strike in focus/)).toBeInTheDocument();
  });

  it("renders an awaiting message when there is no qualification", () => {
    render(<RecommendedTradeCard qualification={null} />);

    expect(screen.getByText("Awaiting engine data…")).toBeInTheDocument();
  });
});
