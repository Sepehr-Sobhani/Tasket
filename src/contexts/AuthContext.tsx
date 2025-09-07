"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useSession, signOut } from "next-auth/react";

interface User {
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

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  logout: () => void;
  refreshUser: (_newToken?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const createUserFromSession = useCallback((backendUserId: string) => {
    const userData: User = {
      id: backendUserId,
      username:
        session?.user?.name || session?.user?.email?.split("@")[0] || "user",
      email: session?.user?.email || "",
      fullName: session?.user?.name || undefined,
      avatarUrl: session?.user?.image || undefined,
      isActive: true,
      isVerified: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setUser(userData);
    setToken("nextauth-session");
    setIsLoading(false);
  }, [session]);

  useEffect(() => {
    if (status === "loading") {
      setIsLoading(true);
      return;
    }

    // @ts-ignore - NextAuth session type compatibility
    if (status === "authenticated" && session?.user?.id) {
      // Create user object from NextAuth session data
      // @ts-ignore - NextAuth session type compatibility
      createUserFromSession(session.user.id);
    } else {
      // User is not authenticated - clear any existing data
      setUser(null);
      setToken(null);
      setIsLoading(false);
    }
  }, [session, status, createUserFromSession]);

  const logout = async () => {
    await signOut({ callbackUrl: "/" });
    setUser(null);
    setToken(null);
  };

  const refreshUser = async (_newToken?: string) => {
    if (_newToken) {
      setToken(_newToken);
    }

    // @ts-ignore - NextAuth session type compatibility
    if (session?.user?.id) {
      // @ts-ignore - NextAuth session type compatibility
      createUserFromSession(session.user.id);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading: isLoading || status === "loading",
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
