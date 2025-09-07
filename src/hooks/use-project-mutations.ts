import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Project } from "./use-dashboard";

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description?: string;
      visibility: "public" | "private";
    }) => api.projects.create(data),
    onSuccess: (newProject: Project) => {
      // Optimistically update the projects cache
      queryClient.setQueryData(["projects"], (old: Project[] | undefined) => {
        if (!old) {
          return [newProject];
        }
        return [newProject, ...old];
      });

      // Also invalidate to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ["projects"] });

      // Invalidate dashboard stats
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
      api.projects.update(id, data),
    onSuccess: (updatedProject: Project) => {
      // Update the projects cache
      queryClient.setQueryData(["projects"], (old: Project[] | undefined) => {
        if (!old) return [updatedProject];
        return old.map((project) =>
          project.id === updatedProject.id ? updatedProject : project
        );
      });

      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.projects.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from projects cache
      queryClient.setQueryData(["projects"], (old: Project[] | undefined) => {
        if (!old) return [];
        return old.filter((project) => project.id !== deletedId);
      });

      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });
}
