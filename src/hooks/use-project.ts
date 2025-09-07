import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Project } from "./use-dashboard";

export function useProject(projectId: string) {
  return useQuery<Project>({
    queryKey: ["project", projectId],
    queryFn: () => api.projects.getById(projectId),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => api.projects.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
