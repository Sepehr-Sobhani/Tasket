import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type DashboardStats = components["schemas"]["DashboardStats"];
type Project = components["schemas"]["Project"];

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.dashboard.getStats(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useProjects() {
  return useQuery<{ projects: Project[] }>({
    queryKey: ["projects"],
    queryFn: async () => {
      const projects = await api.projects.getAll();
      return { projects };
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
