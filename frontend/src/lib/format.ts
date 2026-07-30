// Display-only formatting helpers. These never compute engine values — the API
// already provides spot change, percentages, classifications, etc. These only
// format already-computed values for the screen.

const GROUPER = new Intl.NumberFormat("en-IN");

/** Group an integer with thousands separators, e.g. 40911 -> "40,911". */
export function formatInt(value: number): string {
  return GROUPER.format(value);
}

/** Prefix a signed integer with + / - for OI deltas, e.g. 1400 -> "+1,400". */
export function formatSignedInt(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${GROUPER.format(value)}`;
}

/** Format a decimal string from the API for price display, e.g. "25184.25". */
export function formatDecimal(value: string | null, fractionDigits = 2): string {
  if (value === null) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return value;
  return n.toLocaleString("en-IN", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
}

/** Format an API-provided signed change string, e.g. "86.25" -> "+86.25". */
export function formatSignedDecimal(value: string | null): string {
  if (value === null) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return value;
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** Format an API-provided percent number, e.g. 0.34 -> "+0.34%". */
export function formatPercent(value: number | null): string {
  if (value === null) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

/** Sign of a numeric-ish value: 1 (up), -1 (down), 0 (flat/unknown). */
export function signOf(value: string | number | null): -1 | 0 | 1 {
  if (value === null) return 0;
  const n = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(n) || n === 0) return 0;
  return n > 0 ? 1 : -1;
}

/** Extract HH:MM:SS from an ISO timestamp for the header clock. */
export function formatClock(iso: string | null): string {
  if (iso === null) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

/** Turn a snake/enum token into Title Case, e.g. "long_buildup" -> "Long Build-up". */
const LABEL_OVERRIDES: Record<string, string> = {
  long_buildup: "Long Build-up",
  short_buildup: "Short Build-up",
  long_unwinding: "Long Unwinding",
  short_covering: "Short Covering",
  oi_change: "OI",
  volume_change: "Volume",
  premium_change: "Premium",
  oi_velocity: "OI Velocity",
};

export function labelize(token: string | null): string {
  if (!token) return "—";
  if (token in LABEL_OVERRIDES) return LABEL_OVERRIDES[token];
  return token
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
