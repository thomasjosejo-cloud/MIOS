import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ParticipationRadar } from "@/components/ParticipationRadar";
import { dashboardFixture, notConnectedFixture } from "@/test/fixtures";

const atm = dashboardFixture.market.atm_strike;

describe("ParticipationRadar", () => {
  it("renders the ATM±2 window anchored on the ATM strike", () => {
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        atmStrike={atm}
        selected={null}
        onSelect={() => {}}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Participation Radar" }),
    ).toBeInTheDocument();
    // Five strike levels centred on ATM (25200) at a 50-point step.
    for (const level of ["ATM+2", "ATM+1", "ATM", "ATM−1", "ATM−2"]) {
      expect(screen.getByText(level)).toBeInTheDocument();
    }
    for (const strike of ["25300", "25250", "25150", "25100"]) {
      expect(screen.getByText(strike)).toBeInTheDocument();
    }
  });

  it("shows each side's classification and percentage changes", () => {
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        atmStrike={atm}
        selected={null}
        onSelect={() => {}}
      />,
    );

    // 25150 CE: long buildup with its OI / premium / volume % changes.
    expect(screen.getByText("Long Build-up")).toBeInTheDocument();
    expect(screen.getByText("+3.54%")).toBeInTheDocument();
    expect(screen.getByText("+9.00%")).toBeInTheDocument();
    expect(screen.getByText("+34.00%")).toBeInTheDocument();
    // A strike outside the traded set shows an empty side, not fabricated data.
    expect(screen.getAllByText("No participation").length).toBeGreaterThan(0);
  });

  it("selects a strike + side when that side block is clicked", async () => {
    const onSelect = vi.fn();
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        atmStrike={atm}
        selected={null}
        onSelect={onSelect}
      />,
    );

    // Clicking the 25150 CE block selects that strike and side.
    await userEvent.click(screen.getByText("Long Build-up"));

    expect(onSelect).toHaveBeenCalledWith({ strike: "25150", option_type: "CE" });
  });

  it("shows a polished empty state when there is no participation", () => {
    render(
      <ParticipationRadar
        rows={[]}
        atmStrike={notConnectedFixture.market.atm_strike}
        selected={null}
        onSelect={() => {}}
      />,
    );

    expect(
      screen.getByText("No meaningful participation detected yet."),
    ).toBeInTheDocument();
  });

  it("keeps CE and PE for the same strike on one row", () => {
    render(
      <ParticipationRadar
        rows={dashboardFixture.participation}
        atmStrike={atm}
        selected={null}
        onSelect={() => {}}
      />,
    );

    // The ATM row (25200) has both a CE and a PE side populated.
    const atmRow = screen.getByText("ATM").closest("tr");
    expect(atmRow).not.toBeNull();
    const row = atmRow as HTMLElement;
    expect(within(row).getByText("Short Covering")).toBeInTheDocument();
    expect(within(row).getByText("Short Build-up")).toBeInTheDocument();
  });
});
