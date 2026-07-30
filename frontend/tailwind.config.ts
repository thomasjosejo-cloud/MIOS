import type { Config } from "tailwindcss";

// Dark-only palette from the Sprint 7 spec.
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0B0F14",
        card: "#121821",
        border: "#1E2733",
        accent: "#3B82F6",
        bullish: "#16A34A",
        bearish: "#DC2626",
        muted: "#8A97A8",
        foreground: "#E5E7EB",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
