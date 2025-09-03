import createClient from "openapi-fetch";
import type { paths } from "@/types/api";
import { config } from "./config";

// Helper function to get auth headers
export function getAuthHeaders(token?: string): Record<string, string> {
  const authToken =
    token ||
    (typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null);

  if (!authToken) {
    return {};
  }

  return {
    Authorization: `Bearer ${authToken}`,
  };
}

// For NextAuth integration, we'll need to get the session token
export async function getNextAuthHeaders(): Promise<Record<string, string>> {
  try {
    // This will be used when we have NextAuth session
    // For now, we'll use the traditional token approach
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (!token) {
      return {};
    }

    return {
      Authorization: `Bearer ${token}`,
    };
  } catch (error) {
    console.error("Error getting auth headers:", error);
    return {};
  }
}

// Create the openapi-fetch client
const client = createClient<paths>({
  baseUrl: config.api.baseUrl,
});

// Helper to add auth headers to requests
const withAuth = async (requestInit?: RequestInit) => {
  const authHeaders = await getNextAuthHeaders();
  return {
    ...requestInit,
    headers: {
      ...requestInit?.headers,
      ...authHeaders,
    },
  };
};

// Type-safe API functions using openapi-fetch
export const api = {
  // Projects
  projects: {
    getAll: async () => {
      const { data, error } = await client.GET("/api/v1/projects/", {
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return data;
    },
    getById: async (id: string) => {
      const { data, error } = await client.GET(
        "/api/v1/projects/{project_id}",
        {
          params: { path: { project_id: id } },
          headers: await getNextAuthHeaders(),
        }
      );
      if (error) throw error;
      return data;
    },
    getDefault: async () => {
      const { data, error } = await client.GET("/api/v1/projects/default", {
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return data;
    },
    create: async (data: any) => {
      const { data: response, error } = await client.POST("/api/v1/projects/", {
        body: data,
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return response;
    },
    update: async (id: string, data: any) => {
      const { data: response, error } = await client.PUT(
        "/api/v1/projects/{project_id}",
        {
          params: { path: { project_id: id } },
          body: data,
          headers: await getNextAuthHeaders(),
        }
      );
      if (error) throw error;
      return response;
    },
    delete: async (id: string) => {
      const { data, error } = await client.DELETE(
        "/api/v1/projects/{project_id}",
        {
          params: { path: { project_id: id } },
          headers: await getNextAuthHeaders(),
        }
      );
      if (error) throw error;
      return data;
    },
  },

  // Users
  users: {
    getAll: async () => {
      const { data, error } = await client.GET("/api/v1/users/", {
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return data;
    },
    getById: async (id: string) => {
      const { data, error } = await client.GET("/api/v1/users/{user_id}", {
        params: { path: { user_id: parseInt(id) } },
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return data;
    },
    getMe: async () => {
      const { data, error } = await client.GET("/api/v1/auth/me", {
        headers: await getNextAuthHeaders(),
      });
      if (error) throw error;
      return data;
    },
    update: async (id: string, data: any) => {
      // Note: PUT endpoint for users might not exist in current API schema
      // Using fallback approach for now
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/${id}`, {
        method: "PUT",
        headers: {
          ...(await getNextAuthHeaders()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      return response.json();
    },
  },

  // Auth
  auth: {
    login: async (data: any) => {
      const { data: response, error } = await client.POST(
        "/api/v1/auth/login",
        {
          body: data,
        }
      );
      if (error) throw error;
      return response;
    },
    register: async (data: any) => {
      const { data: response, error } = await client.POST(
        "/api/v1/auth/register",
        {
          body: data,
        }
      );
      if (error) throw error;
      return response;
    },
    logout: async () => {
      // Note: This endpoint might not exist in the current API schema
      // Using a fallback approach for now
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/auth/jwt/logout`,
        {
          method: "POST",
          headers: await getNextAuthHeaders(),
        }
      );
      return response.json();
    },
  },

  // Dashboard
  dashboard: {
    getStats: async () => {
      const { data, error } = await client.GET(
        "/api/v1/projects/stats/dashboard",
        {
          headers: await getNextAuthHeaders(),
        }
      );
      if (error) throw error;
      return data;
    },
  },
};

// Export the client for direct use if needed
export { client };
