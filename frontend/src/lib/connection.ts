import type { ConnectionState } from "@/types/dashboard";

/** Backend endpoint that begins the Fyers OAuth flow (full navigation). */
export const FYERS_LOGIN_URL = "/api/v1/fyers/login";

export type ConnectionTone = "connected" | "connecting" | "error" | "idle";

export interface ConnectionMeta {
  /** Short label for the header chip. */
  label: string;
  /** Heading shown on the connection gate. */
  title: string;
  /** Supporting sentence on the connection gate. */
  description: string;
  tone: ConnectionTone;
  /** Whether to show the "Connect to Fyers" button. */
  showConnect: boolean;
}

/** Presentation for each of the five backend connection states. */
export const CONNECTION_META: Record<ConnectionState, ConnectionMeta> = {
  connected: {
    label: "Connected",
    title: "Connected",
    description: "",
    tone: "connected",
    showConnect: false,
  },
  connecting: {
    label: "Connecting",
    title: "Connecting…",
    description: "Completing Fyers authentication.",
    tone: "connecting",
    showConnect: false,
  },
  session_expired: {
    label: "Session Expired",
    title: "Session Expired",
    description:
      "Your Fyers session has expired. Reconnect to resume live data.",
    tone: "error",
    showConnect: true,
  },
  authentication_failed: {
    label: "Authentication Failed",
    title: "Authentication Failed",
    description: "Fyers authentication did not complete. Please try again.",
    tone: "error",
    showConnect: true,
  },
  not_connected: {
    label: "Not Connected",
    title: "Not Connected to Fyers",
    description:
      "Connect your Fyers account to start receiving live option-chain intelligence.",
    tone: "idle",
    showConnect: true,
  },
};

export function toneClass(tone: ConnectionTone): string {
  switch (tone) {
    case "connected":
      return "text-bullish";
    case "connecting":
      return "text-accent";
    case "error":
      return "text-bearish";
    default:
      return "text-muted";
  }
}

export function toneDotClass(tone: ConnectionTone): string {
  switch (tone) {
    case "connected":
      return "bg-bullish live-dot";
    case "connecting":
      return "bg-accent live-dot";
    case "error":
      return "bg-bearish";
    default:
      return "bg-muted";
  }
}
