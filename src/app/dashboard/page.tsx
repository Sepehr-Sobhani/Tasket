"use client";

import { Suspense, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout";
import { DashboardSkeleton } from "@/components/skeletons/dashboard-skeleton";
import { DashboardContent } from "@/components/dashboard/dashboard-content";

export default function DashboardPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Clear projects cache to force fresh fetch and show skeleton
  useEffect(() => {
    queryClient.removeQueries({ queryKey: ["projects"] });
  }, [queryClient]);

  if (!user) return null;

  return (
    <AppLayout user={user}>
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardContent user={user} />
      </Suspense>
    </AppLayout>
  );
}
