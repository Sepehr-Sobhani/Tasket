"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useSession, signOut } from "next-auth/react";
import { AuthService, User } from "@/lib/auth";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => void;
  refreshUser: (newToken?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (status === "loading") {
      setIsLoading(true);
      return;
    }

    if (status === "authenticated" && session?.user?.id) {
      // User is authenticated with NextAuth, get backend user data
      fetchBackendUser(session.user.id);
    } else {
      // User is not authenticated - clear any existing data
      setUser(null);
      setToken(null);
      // Clear any stale tokens from localStorage
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("nextauth_session_token");
      }
      setIsLoading(false);
    }
  }, [session, status]);

  const fetchBackendUser = async (backendUserId: string) => {
    try {
      // Store the backend user ID for token exchange
      localStorage.setItem("nextauth_session_token", backendUserId);

      // Get API URL from config
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        // Fallback to creating user without backend token exchange
        createUserFromSession(backendUserId);
        return;
      }

      // Exchange NextAuth session for JWT token
      const response = await fetch(`${apiUrl}/api/v1/auth/exchange-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: backendUserId }),
      });

      if (response.ok) {
        const tokenData = await response.json();
        localStorage.setItem("access_token", tokenData.access_token);
        setToken(tokenData.access_token);
      } else {
        setToken("nextauth-session");
      }

      // Create user object from session data
      createUserFromSession(backendUserId);
    } catch (error) {
      // Still create user from session even if backend is unavailable
      createUserFromSession(backendUserId);
    } finally {
      setIsLoading(false);
    }
  };

  const createUserFromSession = (backendUserId: string) => {
    const userData: User = {
      id: backendUserId,
      username:
        session?.user?.name || session?.user?.email?.split("@")[0] || "user",
      email: session?.user?.email || "",
      full_name: session?.user?.name || undefined,
      avatar_url: session?.user?.image || undefined,
      bio: undefined,
      github_id: undefined,
      github_username: undefined,
      role: "member",
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setUser(userData);
  };

  const login = async (username: string, password: string) => {
    try {
      const authData = await AuthService.login({ username, password });
      setToken(authData.access_token);
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      await AuthService.register(userData);
      // After registration, user needs to login
    } catch (error) {
      throw error;
    }
  };

  const loginWithGitHub = async () => {
    // This will be handled by NextAuth
    throw new Error("Use NextAuth signIn instead");
  };

  const loginWithGoogle = async () => {
    // This will be handled by NextAuth
    throw new Error("Use NextAuth signIn instead");
  };

  const logout = async () => {
    // Clear all tokens from localStorage
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("nextauth_session_token");
    }

    await signOut({ callbackUrl: "/" });
    setUser(null);
    setToken(null);
  };

  const refreshUser = async (newToken?: string) => {
    if (newToken) {
      setToken(newToken);
    }

    if (session?.user?.id) {
      await fetchBackendUser(session.user.id);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading: isLoading || status === "loading",
    login,
    register,
    loginWithGitHub,
    loginWithGoogle,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
