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
