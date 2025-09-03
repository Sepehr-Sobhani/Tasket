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
    // First try to get JWT token from localStorage
    const jwtToken =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (jwtToken) {
      return {
        Authorization: `Bearer ${jwtToken}`,
      };
    }

    // If no JWT token, try to exchange NextAuth session for JWT
    if (typeof window !== "undefined") {
      const nextAuthToken = localStorage.getItem("nextauth_session_token");
      if (nextAuthToken) {
        try {
          const response = await fetch(
            `${config.api.baseUrl}/api/v1/auth/exchange-token`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ user_id: nextAuthToken }),
            }
          );

          if (response.ok) {
            const tokenData = await response.json();
            localStorage.setItem("access_token", tokenData.access_token);
            return {
              Authorization: `Bearer ${tokenData.access_token}`,
            };
          } else {
            // If token exchange fails, clear the stored tokens
            localStorage.removeItem("nextauth_session_token");
            localStorage.removeItem("access_token");
          }
        } catch (error) {
          // Clear tokens on error
          localStorage.removeItem("nextauth_session_token");
          localStorage.removeItem("access_token");
        }
      }
    }

    return {};
  } catch (error) {
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

// Helper function to handle 401 errors and refresh tokens
export async function handleAuthError(response: Response): Promise<boolean> {
  if (response.status === 401) {
    // Clear invalid tokens
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("nextauth_session_token");
    }

    // Redirect to login if we're not already there
    if (
      typeof window !== "undefined" &&
      !window.location.pathname.startsWith("/auth")
    ) {
      window.location.href = "/";
    }

    return true; // Indicates we handled the error
  }
  return false; // Error not handled
}

// Export the client for direct use if needed
export { client };
