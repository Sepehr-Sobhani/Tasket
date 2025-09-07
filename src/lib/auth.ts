import { config } from "./config";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  github_id?: string;
  github_username?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

class AuthService {
  // Traditional login (for email/password authentication)
  static async login(credentials: {
    username: string;
    password: string;
  }): Promise<AuthToken> {
    const response = await fetch(`${config.api.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }

    const tokenData = await response.json();

    // Store tokens
    this.setTokensToStorage({
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token || tokenData.access_token,
    });

    return tokenData;
  }

  // Register new user
  static async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }): Promise<User> {
    const response = await fetch(`${config.api.baseUrl}/api/v1/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }

    return await response.json();
  }

  // Get current user (for traditional auth)
  static async getCurrentUser(): Promise<User> {
    const accessToken = this.getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error("No access token found");
    }

    const response = await fetch(`${config.api.baseUrl}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication failed");
      }
      throw new Error("Failed to get user data");
    }

    return await response.json();
  }

  // Token storage methods (for traditional auth)
  static getAccessTokenFromStorage(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  static getRefreshTokenFromStorage(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  }

  static setTokensToStorage(tokens: {
    accessToken: string;
    refreshToken: string;
  }): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("access_token", tokens.accessToken);
    localStorage.setItem("refresh_token", tokens.refreshToken);
  }

  static setAccessTokenToStorage(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("access_token", token);
  }

  static removeTokensFromStorage(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  // Utility methods
  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  static getTokenExpiry(token: string): Date | null {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return new Date(payload.exp * 1000);
    } catch {
      return null;
    }
  }
}

export { AuthService };
