import { AlertTriangle, Loader2 } from "lucide-react";

import { Card } from "@/components/ui/card";

/** Shown when the dashboard cannot be reached. TanStack Query keeps retrying. */
export function ErrorState() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="flex max-w-sm flex-col items-center gap-3 p-8 text-center">
        <AlertTriangle className="h-8 w-8 text-bearish" aria-hidden />
        <div>
          <p className="text-lg font-semibold text-foreground">
            Engine unavailable.
          </p>
          <p className="mt-1 flex items-center justify-center gap-2 text-sm text-muted">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Retrying…
          </p>
        </div>
      </Card>
    </div>
  );
}
