import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ParticipationRadar } from "@/components/ParticipationRadar";
import { dashboardFixture } from "@/test/fixtures";

describe("ParticipationRadar", () => {
  it("renders ranked strikes with classification and percentages", () => {
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        selected={null}
        onSelect={() => {}}
      />,
    );

    expect(screen.getByRole("heading", { name: "Participation Radar" })).toBeInTheDocument();
    // Rank 1 strike from the fixture, with its classification and OI %.
    expect(screen.getByText("25000")).toBeInTheDocument();
    expect(screen.getByText("Short Build-up")).toBeInTheDocument();
    expect(screen.getByText("+5.35%")).toBeInTheDocument();
  });

  it("selects a strike when its row is clicked", async () => {
    const onSelect = vi.fn();
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        selected={null}
        onSelect={onSelect}
      />,
    );

    await userEvent.click(screen.getByText("25150"));

    expect(onSelect).toHaveBeenCalledWith({ strike: "25150", option_type: "CE" });
  });

  it("shows a polished empty state when there is no participation", () => {
    render(
      <ParticipationRadar rows={[]} selected={null} onSelect={() => {}} />,
    );

    expect(
      screen.getByText("No meaningful participation detected yet."),
    ).toBeInTheDocument();
  });
});
