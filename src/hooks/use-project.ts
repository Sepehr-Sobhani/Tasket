import { useSuspenseQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Project } from "@/types/api-common";

export function useProject(projectId: string) {
  return useSuspenseQuery<Project>({
    queryKey: ["project", projectId],
    queryFn: () => api.projects.getById(projectId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProjects() {
  return useSuspenseQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => api.projects.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    // Force suspense to show on first load
    refetchOnMount: true,
  });
}
