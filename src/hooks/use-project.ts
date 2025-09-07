import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type Project = components["schemas"]["Project"];
type User = components["schemas"]["User"];

export function useProject(projectId: string) {
  return useQuery<Project>({
    queryKey: ["project", projectId],
    queryFn: () => api.projects.getById(projectId),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDefaultProject() {
  return useQuery<Project>({
    queryKey: ["default-project"],
    queryFn: () => api.projects.getDefault(),
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
