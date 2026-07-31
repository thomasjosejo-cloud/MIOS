import { screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "@/App";
import { dashboardFixture, notConnectedFixture } from "@/test/fixtures";
import { renderWithClient } from "@/test/renderWithClient";

function mockFetchOnce(payload: unknown, ok = true): void {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 503,
      headers: { get: () => "application/json" },
      json: async () => payload,
    }),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("App", () => {
  it("shows a skeleton before the first response", () => {
    // fetch never resolves within this test's first tick.
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(new Promise(() => {})));
    renderWithClient(<App />);

    expect(screen.getByTestId("dashboard-skeleton")).toBeInTheDocument();
  });

  it("renders the dashboard once data arrives", async () => {
    mockFetchOnce(dashboardFixture);
    renderWithClient(<App />);

    expect(await screen.findByText("Trade Qualified")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Market Dominance" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Option Chain" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "What Is Happening Now" }),
    ).toBeInTheDocument();
    // Evidence items are rendered exactly as received from the API.
    expect(screen.getByText("Buyers dominant")).toBeInTheDocument();
  });

  it("shows the connection gate when not connected to Fyers", async () => {
    mockFetchOnce(notConnectedFixture);
    renderWithClient(<App />);

    expect(
      await screen.findByText("Not Connected to Fyers"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Connect to Fyers" }),
    ).toHaveAttribute("href", "/api/v1/fyers/login");
    // The dashboard (qualified trade) is not shown while disconnected.
    expect(screen.queryByText("Trade Qualified")).not.toBeInTheDocument();
  });

  it("shows the error state when the request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));
    renderWithClient(<App />);

    expect(await screen.findByText("Engine unavailable.")).toBeInTheDocument();
    expect(screen.getByText("Retrying…")).toBeInTheDocument();
  });

  it("refetches on the 2 second interval", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => "application/json" },
      json: async () => dashboardFixture,
    });
    vi.stubGlobal("fetch", fetchMock);

    renderWithClient(<App />);

    // First fetch on mount.
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    // A second fetch fires after the 2s poll interval.
    await waitFor(() => expect(fetchMock.mock.calls.length).toBeGreaterThanOrEqual(2), {
      timeout: 4000,
    });
  });
});
