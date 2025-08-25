import { config } from "./config";

// Helper function to get auth headers
export function getAuthHeaders(token?: string): Record<string, string> {
  const authToken =
    token ||
    (typeof window !== "undefined" ? localStorage.getItem("auth_token") : null);

  if (!authToken) {
    return {};
  }

  return {
    Authorization: `Bearer ${authToken}`,
  };
}

// Type-safe API functions using fetch with proper typing
export const api = {
  // Projects
  projects: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/projects/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/projects/${id}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    create: async (data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/projects/`, {
        method: "POST",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/projects/${id}`,
        {
          method: "PUT",
          headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );
      return response.json();
    },
    delete: async (id: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/projects/${id}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
  },

  // Tasks
  tasks: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tasks/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getByProject: async (projectId: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/tasks/project/${projectId}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tasks/${id}`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    create: async (data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tasks/`, {
        method: "POST",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tasks/${id}`, {
        method: "PUT",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    delete: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tasks/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
      return response.json();
    },
  },

  // Epics
  epics: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/epics/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getByProject: async (projectId: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/epics/project/${projectId}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/epics/${id}`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    create: async (data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/epics/`, {
        method: "POST",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/epics/${id}`, {
        method: "PUT",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    delete: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/epics/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
      return response.json();
    },
  },

  // Tags
  tags: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tags/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getByProject: async (projectId: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/tags/project/${projectId}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tags/${id}`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    create: async (data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tags/`, {
        method: "POST",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tags/${id}`, {
        method: "PUT",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    delete: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/tags/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
      return response.json();
    },
  },

  // Users
  users: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/${id}`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getMe: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/auth/me`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/${id}`, {
        method: "PUT",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
  },

  // Auth
  auth: {
    login: async (data: any) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/auth/jwt/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams(data),
        }
      );
      return response.json();
    },
    register: async (data: any) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );
      return response.json();
    },
    logout: async () => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/auth/jwt/logout`,
        {
          method: "POST",
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
  },

  // Notifications
  notifications: {
    getAll: async (limit = 20, offset = 0) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/notifications/?limit=${limit}&offset=${offset}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    markAsRead: async (notificationId: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/notifications/${notificationId}/read`,
        {
          method: "PATCH",
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    markAllAsRead: async () => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/notifications/mark-all-read`,
        {
          method: "PATCH",
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
  },

  // Milestones
  milestones: {
    getAll: async () => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/milestones/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    },
    getByProject: async (projectId: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/milestones/project/${projectId}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    getById: async (id: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/milestones/${id}`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
    create: async (data: any) => {
      const response = await fetch(`${config.api.baseUrl}/api/v1/milestones/`, {
        method: "POST",
        headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: number, data: any) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/milestones/${id}`,
        {
          method: "PUT",
          headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );
      return response.json();
    },
    delete: async (id: number) => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/milestones/${id}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
  },

  // Dashboard
  dashboard: {
    getStats: async () => {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/projects/stats/dashboard`,
        {
          headers: getAuthHeaders(),
        }
      );
      return response.json();
    },
  },
};
