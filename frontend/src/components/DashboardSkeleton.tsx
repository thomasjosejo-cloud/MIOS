import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/** First-load skeleton shown before the first successful poll. */
export function DashboardSkeleton() {
  return (
    <div className="space-y-4" data-testid="dashboard-skeleton">
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="mt-3 h-10 w-40" />
          <Skeleton className="mt-4 h-6 w-56" />
          <Skeleton className="mt-2 h-4 w-full" />
        </Card>
        <Card className="p-5">
          <Skeleton className="h-4 w-24" />
          <div className="mt-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
        </Card>
      </div>
      <Card className="p-5">
        <Skeleton className="h-4 w-20" />
        <div className="mt-4 space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-4 w-3/4" />
          ))}
        </div>
      </Card>
      <Card className="p-5">
        <Skeleton className="h-4 w-24" />
        <div className="mt-4 space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-6 w-full" />
          ))}
        </div>
      </Card>
    </div>
  );
}
