import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConnectionGate } from "@/components/ConnectionGate";

describe("ConnectionGate", () => {
  it("shows Not Connected with a Connect button", () => {
    render(<ConnectionGate state="not_connected" />);

    expect(screen.getByText("Not Connected to Fyers")).toBeInTheDocument();
    const link = screen.getByRole("link", { name: "Connect to Fyers" });
    expect(link).toHaveAttribute("href", "/api/v1/fyers/login");
  });

  it("shows Session Expired with a reconnect button", () => {
    render(<ConnectionGate state="session_expired" />);

    expect(screen.getByText("Session Expired")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Connect to Fyers" }),
    ).toBeInTheDocument();
  });

  it("shows Authentication Failed with a retry button", () => {
    render(<ConnectionGate state="authentication_failed" />);

    expect(screen.getByText("Authentication Failed")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Connect to Fyers" }),
    ).toBeInTheDocument();
  });

  it("shows Connecting without a button", () => {
    render(<ConnectionGate state="connecting" />);

    expect(screen.getByText("Connecting…")).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: "Connect to Fyers" }),
    ).not.toBeInTheDocument();
  });
});
