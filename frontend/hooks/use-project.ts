import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type Project = components["schemas"]["Project"];
type Epic = components["schemas"]["Epic"];
type Task = components["schemas"]["Task"];
type Tag = components["schemas"]["Tag"];
type User = components["schemas"]["User"];

export function useProject(projectId: number) {
  return useQuery<Project>({
    queryKey: ["project", projectId],
    queryFn: () => api.projects.getById(projectId),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProjectEpics(projectId: number) {
  return useQuery<{ epics: Epic[] }>({
    queryKey: ["project-epics", projectId],
    queryFn: () => api.epics.getByProject(projectId),
    enabled: !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useProjectTasks(projectId: number) {
  return useQuery<{ tasks: Task[] }>({
    queryKey: ["project-tasks", projectId],
    queryFn: () => api.tasks.getByProject(projectId),
    enabled: !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useProjectTags(projectId: number) {
  return useQuery<{ tags: Tag[] }>({
    queryKey: ["project-tags", projectId],
    queryFn: () => api.tags.getByProject(projectId),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUsers() {
  return useQuery<{ users: User[] }>({
    queryKey: ["users"],
    queryFn: () => api.users.getAll(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
