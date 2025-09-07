// Common API types and interfaces

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  avatarUrl?: string;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  visibility: "public" | "private";
  isActive: boolean;
  isDefault: boolean;
  githubRepoId?: string;
  githubRepoName?: string;
  githubRepoOwner?: string;
  createdAt: string;
  updatedAt?: string;
  memberCount: number;
  owner?: {
    id: string;
    username: string;
    fullName?: string;
    avatarUrl?: string;
  };
}

export interface ProjectMember {
  id: string;
  projectId: string;
  userId: string;
  role: "OWNER" | "ADMIN" | "MEMBER";
  joinedAt: string;
  user?: User;
}

export interface DashboardStats {
  totalProjects: number;
  activeProjects: number;
  totalMembers: number;
  recentActivity: number;
}
