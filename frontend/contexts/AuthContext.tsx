"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, AuthToken, AuthService } from "@/lib/auth";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  loginWithGitHub: () => void;
  loginWithGoogle: () => void;
  logout: () => void;
  refreshUser: (newToken?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const storedToken = AuthService.getTokenFromStorage();

      if (storedToken && !AuthService.isTokenExpired(storedToken)) {
        setToken(storedToken);
        const userData = await AuthService.getCurrentUser(storedToken);
        setUser(userData);
      }
    } catch (error) {
      console.error("Failed to initialize auth:", error);
      AuthService.removeTokenFromStorage();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const authData = await AuthService.login({ username, password });

      AuthService.setTokenToStorage(authData.access_token);
      setToken(authData.access_token);

      const userData = await AuthService.getCurrentUser(authData.access_token);
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

  const loginWithGitHub = () => {
    const githubUrl = AuthService.getGitHubOAuthURL();
    window.location.href = githubUrl;
  };

  const loginWithGoogle = () => {
    const googleUrl = AuthService.getGoogleOAuthURL();
    window.location.href = googleUrl;
  };

  const logout = () => {
    AuthService.removeTokenFromStorage();
    setToken(null);
    setUser(null);
  };

  const refreshUser = async (newToken?: string) => {
    const tokenToUse = newToken || token;
    if (tokenToUse) {
      try {
        // Update token state if a new token is provided
        if (newToken) {
          setToken(newToken);
        }

        const userData = await AuthService.getCurrentUser(tokenToUse);
        setUser(userData);
      } catch (error) {
        console.error("Failed to refresh user:", error);
        logout();
      }
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
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
