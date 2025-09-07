import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      {/* Welcome Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
        </div>
      </div>

      {/* Recent Projects Skeleton */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-9 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="border-primary/20 bg-primary/5">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-4 w-4" />
                </div>
                <Skeleton className="h-4 w-full mt-2" />
                <Skeleton className="h-4 w-3/4 mt-1" />
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                  <div className="flex items-center space-x-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-12" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
