import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { OptionChain } from "@/components/OptionChain";
import { rowDomId } from "@/lib/rows";
import { dashboardFixture } from "@/test/fixtures";

describe("OptionChain", () => {
  it("renders every column header", () => {
    render(<OptionChain rows={dashboardFixture.option_chain} highlightedRowId={null} />);

    for (const col of [
      "Strike",
      "Type",
      "Premium",
      "OI",
      "OI Δ",
      "Volume",
      "Classification",
      "Unusual",
      "Signal",
    ]) {
      expect(screen.getByRole("columnheader", { name: col })).toBeInTheDocument();
    }
  });

  it("renders one row per strike with formatted values", () => {
    render(<OptionChain rows={dashboardFixture.option_chain} highlightedRowId={null} />);

    const row = screen.getByTestId(rowDomId("25150", "CE"));
    expect(within(row).getByText("25150")).toBeInTheDocument();
    expect(within(row).getByText("142.50")).toBeInTheDocument();
    expect(within(row).getByText("40,911")).toBeInTheDocument();
    expect(within(row).getByText("+1,400")).toBeInTheDocument();
  });

  it("marks the qualified strike from the qualification data", () => {
    render(
      <OptionChain
        rows={dashboardFixture.option_chain}
        highlightedRowId={null}
        qualification={dashboardFixture.qualification}
      />,
    );

    // 25150 CE is the qualified strike -> green highlight + "Qualified".
    const qualified = screen.getByTestId(rowDomId("25150", "CE"));
    expect(qualified.className).toContain("bg-bullish");
    expect(within(qualified).getByText("Qualified")).toBeInTheDocument();

    const other = screen.getByTestId(rowDomId("25000", "PE"));
    expect(other.className).not.toContain("bg-bullish");
  });
});
