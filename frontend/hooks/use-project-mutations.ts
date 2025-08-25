import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type Epic = components["schemas"]["Epic"];
type Task = components["schemas"]["Task"];

export function useCreateEpic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      title: string;
      description: string;
      project_id: number;
    }) => api.epics.create(data),
    onSuccess: (newEpic, variables) => {
      // Update the epics cache
      queryClient.setQueryData(
        ["project-epics", variables.project_id],
        (old: { epics: Epic[] } | undefined) => {
          if (!old?.epics) return old;
          return {
            ...old,
            epics: [...old.epics, newEpic],
          };
        }
      );
    },
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      title: string;
      description: string;
      priority: string;
      project_id: number;
      assignee_id?: number;
      epic_id?: number;
    }) => api.tasks.create(data),
    onSuccess: (newTask, variables) => {
      // Update the tasks cache
      queryClient.setQueryData(
        ["project-tasks", variables.project_id],
        (old: { tasks: Task[] } | undefined) => {
          if (!old?.tasks) return old;
          return {
            ...old,
            tasks: [...old.tasks, newTask],
          };
        }
      );
    },
  });
}

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
