import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { OptionChain } from "@/components/OptionChain";
import { TopCandidates } from "@/components/TopCandidates";
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
      "Recommended",
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

  it("marks the recommended strike", () => {
    render(<OptionChain rows={dashboardFixture.option_chain} highlightedRowId={null} />);

    const recommended = screen.getByTestId(rowDomId("25150", "CE"));
    expect(recommended.className).toContain("bg-accent");
    const notRecommended = screen.getByTestId(rowDomId("25000", "PE"));
    expect(notRecommended.className).not.toContain("bg-accent");
  });
});

describe("TopCandidates", () => {
  it("scrolls to the strike row when a candidate is clicked", async () => {
    const onSelect = vi.fn();
    render(
      <TopCandidates
        candidates={dashboardFixture.top_candidates}
        onSelect={onSelect}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: /25200/ }));

    expect(onSelect).toHaveBeenCalledWith(rowDomId("25200", "CE"));
  });
});
