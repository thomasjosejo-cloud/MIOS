import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ParticipationStatus } from "@/components/ParticipationStatus";
import { dashboardFixture, notConnectedFixture } from "@/test/fixtures";

describe("ParticipationStatus", () => {
  it("shows the recommended strike's participation and market control", () => {
    render(
      <ParticipationStatus
        qualification={dashboardFixture.qualification}
        participation={dashboardFixture.participation}
        control={dashboardFixture.context?.controlling_side ?? null}
      />,
    );

    expect(screen.getByText("Participation Status")).toBeInTheDocument();
    // Recommended strike is 25150 CE (long buildup) — its row in participation.
    expect(screen.getByText("25150")).toBeInTheDocument();
    expect(screen.getByText("Long Build-up")).toBeInTheDocument();
    expect(screen.getByText("+3.54%")).toBeInTheDocument(); // OI %
    expect(screen.getByText("+9.00%")).toBeInTheDocument(); // Premium %
    expect(screen.getByText("+34.00%")).toBeInTheDocument(); // Volume %
    // Market Control comes from the market context's controlling side.
    expect(screen.getByText("Bulls")).toBeInTheDocument();
  });

  it("degrades gracefully when there is no recommended strike", () => {
    render(
      <ParticipationStatus
        qualification={notConnectedFixture.qualification}
        participation={notConnectedFixture.participation}
        control={null}
      />,
    );

    expect(
      screen.getByText("No recommended strike to analyse yet."),
    ).toBeInTheDocument();
  });
});
