import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth-options";
import type { ProjectCreateInput } from "@/lib/validations/project";

// Helper function to get auth headers for client-side requests
export function getAuthHeaders(): Record<string, string> {
  // For client-side requests, we'll use NextAuth session
  // This will be handled by the middleware
  return {};
}

// Helper function to get auth headers for server-side requests
export async function getServerAuthHeaders(): Promise<Record<string, string>> {
  const session = await getServerSession(authOptions);

  // @ts-ignore - NextAuth session type compatibility
  if (!session?.user?.id) {
    return {};
  }

  return {
    // @ts-ignore - NextAuth session type compatibility
    "x-user-id": session.user.id,
  };
}

// API client functions
export const api = {
  // Projects
  projects: {
    getAll: async () => {
      const response = await fetch("/api/projects");
      if (!response.ok) {
        if (response.status === 401) {
          // Handle 401 by redirecting to login
          if (
            typeof window !== "undefined" &&
            window.location.pathname !== "/"
          ) {
            window.location.href = "/";
          }
          throw new Error("Authentication required");
        }
        throw new Error("Failed to fetch projects");
      }
      return response.json();
    },
    getById: async (id: string) => {
      const response = await fetch(`/api/projects/${id}`);
      if (!response.ok) {
        if (response.status === 401) {
          // Handle 401 by redirecting to login
          if (
            typeof window !== "undefined" &&
            window.location.pathname !== "/"
          ) {
            window.location.href = "/";
          }
          throw new Error("Authentication required");
        }
        throw new Error("Failed to fetch project");
      }
      return response.json();
    },
    create: async (data: ProjectCreateInput) => {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        if (response.status === 401) {
          // Handle 401 by redirecting to login
          if (
            typeof window !== "undefined" &&
            window.location.pathname !== "/"
          ) {
            window.location.href = "/";
          }
          throw new Error("Authentication required");
        }
        throw new Error("Failed to create project");
      }
      return response.json();
    },
  },
};

// Helper function to handle 401 errors (kept for backward compatibility)
export async function handleAuthError(response: Response): Promise<boolean> {
  if (response.status === 401) {
    // Redirect to login if we're not already there
    if (typeof window !== "undefined" && window.location.pathname !== "/") {
      window.location.href = "/";
    }

    return true; // Indicates we handled the error
  }
  return false; // Error not handled
}
