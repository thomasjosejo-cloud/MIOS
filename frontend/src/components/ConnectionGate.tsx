import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CONNECTION_META, FYERS_LOGIN_URL, toneClass } from "@/lib/connection";
import { cn } from "@/lib/utils";
import type { ConnectionState } from "@/types/dashboard";

/**
 * Shown in place of the dashboard whenever MIOS is not connected to Fyers.
 * Renders the current connection state and, when appropriate, a
 * "Connect to Fyers" button that starts the OAuth flow. After a successful
 * login the browser returns here and the 2s dashboard poll flips to Connected.
 */
export function ConnectionGate({ state }: { state: ConnectionState }) {
  const meta = CONNECTION_META[state];

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="w-full max-w-md p-8 text-center">
        <div
          className={cn(
            "mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-border",
            toneClass(meta.tone),
          )}
        >
          <span
            className={cn(
              "h-3 w-3 rounded-full bg-current",
              meta.tone === "connecting" && "animate-pulse",
            )}
            aria-hidden
          />
        </div>

        <h2 className={cn("text-lg font-semibold", toneClass(meta.tone))}>
          {meta.title}
        </h2>
        <p className="mt-2 text-sm text-muted">{meta.description}</p>

        {meta.showConnect ? (
          <Button asChild className="mt-6">
            <a href={FYERS_LOGIN_URL}>Connect to Fyers</a>
          </Button>
        ) : meta.tone === "connecting" ? (
          <p className="mt-6 text-xs text-muted">Please wait…</p>
        ) : null}
      </Card>
    </div>
  );
}
