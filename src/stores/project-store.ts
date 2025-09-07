import { create } from "zustand";

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

export interface DashboardStats {
  totalProjects: number;
  uniqueTeamMembers: number;
  activeProjects: number;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  dashboardStats: DashboardStats | null;
  isLoading: boolean;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  setDashboardStats: (stats: DashboardStats | null) => void;
  setLoading: (loading: boolean) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  removeProject: (id: string) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  dashboardStats: null,
  isLoading: false,
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (currentProject) => set({ currentProject }),
  setDashboardStats: (dashboardStats) => set({ dashboardStats }),
  setLoading: (isLoading) => set({ isLoading }),
  addProject: (project) =>
    set((state) => ({ projects: [...state.projects, project] })),
  updateProject: (id, updates) =>
    set((state) => ({
      projects: state.projects.map((project) =>
        project.id === id ? { ...project, ...updates } : project
      ),
      currentProject:
        state.currentProject?.id === id
          ? { ...state.currentProject, ...updates }
          : state.currentProject,
    })),
  removeProject: (id) =>
    set((state) => ({
      projects: state.projects.filter((project) => project.id !== id),
      currentProject:
        state.currentProject?.id === id ? null : state.currentProject,
    })),
}));
