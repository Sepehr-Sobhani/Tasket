"use client";

import { Suspense, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProjectSkeleton } from "@/components/skeletons/project-skeleton";
import { ProjectContent } from "@/components/project/project-content";

export default function ProjectDetailPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Clear project cache to force fresh fetch and show skeleton
  useEffect(() => {
    queryClient.removeQueries({ queryKey: ["project"] });
  }, [queryClient]);

  if (!user) return null;

  return (
    <AppLayout user={user}>
      <Suspense fallback={<ProjectSkeleton />}>
        <ProjectContent user={user} />
      </Suspense>
    </AppLayout>
  );
}
