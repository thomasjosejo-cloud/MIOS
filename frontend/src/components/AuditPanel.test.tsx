import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuditPanel } from "@/components/AuditPanel";
import { auditFixture } from "@/test/fixtures";
import { renderWithClient } from "@/test/renderWithClient";

function mockAudit(): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    headers: { get: () => "application/json" },
    json: async () => auditFixture,
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("AuditPanel", () => {
  it("is collapsed by default and does not fetch until opened", () => {
    const fetchMock = mockAudit();
    renderWithClient(<AuditPanel />);

    expect(screen.getByText("Decision Trace")).toBeInTheDocument();
    // Body hidden; no request made while collapsed.
    expect(screen.queryByText("Per-strike evidence (±ATM)")).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("fetches and renders the decision trace when opened", async () => {
    const fetchMock = mockAudit();
    renderWithClient(<AuditPanel />);

    await userEvent.click(screen.getByRole("button", { name: /Decision Trace/i }));

    // It calls the audit endpoint...
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/market/audit",
        expect.anything(),
      ),
    );
    // ...and renders conclusions next to the raw per-strike evidence.
    expect(await screen.findByText("Per-strike evidence (±ATM)")).toBeInTheDocument();
    expect(screen.getByText(/No contradictions/i)).toBeInTheDocument();
    // A per-strike row from the fixture.
    expect(screen.getByText("25150")).toBeInTheDocument();
  });
});
