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
      console.log("Project created, updating cache:", newProject);

      // Optimistically update the projects cache
      queryClient.setQueryData(
        ["projects"],
        (old: { projects: any[] } | undefined) => {
          console.log("Current cache data:", old);
          if (!old?.projects) {
            console.log("No existing cache, creating new structure");
            return { projects: [newProject] };
          }
          const updated = {
            ...old,
            projects: [newProject, ...old.projects],
          };
          console.log("Updated cache:", updated);
          return updated;
        }
      );

      // Also invalidate to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ["projects"] });

      // Invalidate dashboard stats
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });

      console.log("Cache updated and queries invalidated");
    },
  });
}
