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
  // eslint-disable-next-line no-unused-vars
  setProjects: (projects: Project[]) => void;
  // eslint-disable-next-line no-unused-vars
  setCurrentProject: (project: Project | null) => void;
  // eslint-disable-next-line no-unused-vars
  setDashboardStats: (stats: DashboardStats | null) => void;
  // eslint-disable-next-line no-unused-vars
  setLoading: (loading: boolean) => void;
  // eslint-disable-next-line no-unused-vars
  addProject: (project: Project) => void;
  // eslint-disable-next-line no-unused-vars
  updateProject: (id: string, updates: Partial<Project>) => void;
  // eslint-disable-next-line no-unused-vars
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
