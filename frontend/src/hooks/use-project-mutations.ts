import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description: string;
      visibility: string;
    }) => api.projects.create(data),
    onSuccess: (newProject) => {
      // Optimistically update the projects cache
      queryClient.setQueryData(
        ["projects"],
        (old: { projects: any[] } | undefined) => {
          if (!old?.projects) {
            return { projects: [newProject] };
          }
          const updated = {
            ...old,
            projects: [newProject, ...old.projects],
          };
          return updated;
        }
      );

      // Also invalidate to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ["projects"] });

      // Invalidate dashboard stats
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });
}
