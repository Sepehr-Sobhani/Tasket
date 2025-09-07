import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Project } from "@/types/api-common";
import type { ProjectCreateInput } from "@/lib/validations/project";

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProjectCreateInput) => api.projects.create(data),
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
    },
  });
}
