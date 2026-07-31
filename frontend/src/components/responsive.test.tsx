import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Sidebar } from "@/components/Sidebar";

describe("responsive layout", () => {
  it("hides the sidebar on small screens and shows it from md up", () => {
    const { container } = render(<Sidebar />);
    const aside = container.querySelector("aside");

    expect(aside).not.toBeNull();
    // Tailwind responsive utilities: hidden by default, flex at md.
    expect(aside?.className).toContain("hidden");
    expect(aside?.className).toContain("md:flex");
  });

  it("still exposes navigation entries in the sidebar", () => {
    render(<Sidebar />);

    for (const label of [
      "Dashboard",
      "Trade Status",
      "Option Chain",
      "Engine Status",
    ]) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }
  });
});
