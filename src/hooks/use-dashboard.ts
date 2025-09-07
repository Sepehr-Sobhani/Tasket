import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export interface DashboardStats {
  total_projects: number;
  unique_team_members: number;
  active_projects: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  visibility: "public" | "private";
  isActive: boolean;
  isDefault: boolean;
  githubRepoId?: string | null;
  githubRepoName?: string | null;
  githubRepoOwner?: string | null;
  createdAt: string;
  updatedAt?: string | null;
  memberCount: number;
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.dashboard.getStats(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => api.projects.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
