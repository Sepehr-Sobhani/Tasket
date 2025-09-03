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
      // User is not authenticated
      setUser(null);
      setToken(null);
      setIsLoading(false);
    }
  }, [session, status]);

  const fetchBackendUser = async (backendUserId: string) => {
    try {
      // For NextAuth integration, we'll create a simple user object
      // In a real implementation, you might want to fetch from your backend
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
      setToken("nextauth-session");
    } catch (error) {
      console.error("Error setting user data:", error);
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
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
