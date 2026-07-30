import { Activity, LayoutDashboard, ListTree, Target } from "lucide-react";

import { cn } from "@/lib/utils";

const NAV = [
  { id: "top", label: "Dashboard", icon: LayoutDashboard },
  { id: "recommendation", label: "Recommendation", icon: Target },
  { id: "option-chain", label: "Option Chain", icon: ListTree },
  { id: "engine-status", label: "Engine Status", icon: Activity },
] as const;

/** Smoothly scroll a section into view by id. */
function scrollToSection(id: string): void {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function Sidebar() {
  return (
    <aside className="hidden w-52 shrink-0 flex-col border-r border-border bg-card/40 md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <div className="h-6 w-6 rounded bg-accent/20 text-center text-sm font-bold leading-6 text-accent">
          M
        </div>
        <span className="text-sm font-semibold tracking-wide">MIOS</span>
      </div>
      <nav className="flex flex-col gap-1 p-2">
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => scrollToSection(id)}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-left text-sm text-muted",
              "transition-colors hover:bg-border hover:text-foreground",
            )}
          >
            <Icon className="h-4 w-4" aria-hidden />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
