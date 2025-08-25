"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { AuthService } from "@/lib/auth";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2, Mail, Shield, Users, Zap } from "lucide-react";

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const token = searchParams.get("token");
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        if (error) {
          setError(errorDescription || `Authentication failed: ${error}`);
          setIsLoading(false);
          return;
        }

        if (!token) {
          setError("No authentication token received");
          setIsLoading(false);
          return;
        }

        // Store the token
        AuthService.setTokenToStorage(token);

        // Refresh user data
        await refreshUser(token);

        // Redirect to dashboard
        router.push("/dashboard");
      } catch (err) {
        console.error("Google authentication error:", err);
        setError(err instanceof Error ? err.message : "Authentication failed");
        setIsLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, router, refreshUser]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">
                  T
                </span>
              </div>
              <span className="text-lg font-semibold">Tasket</span>
            </div>
          </div>

          <Card className="w-full shadow-lg border-0 bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <Loader2 className="h-12 w-12 animate-spin text-primary" />
                  <Mail className="absolute inset-0 m-auto h-6 w-6 text-muted-foreground" />
                </div>
              </div>
              <CardTitle className="text-xl">
                Authenticating with Google
              </CardTitle>
              <CardDescription className="text-base">
                Please wait while we complete your sign-in...
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center">
              <div className="flex items-center justify-center space-x-4 text-xs text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Shield className="h-3 w-3" />
                  <span>Secure</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="h-3 w-3" />
                  <span>Team Ready</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Zap className="h-3 w-3" />
                  <span>Fast</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">
                  T
                </span>
              </div>
              <span className="text-lg font-semibold">Tasket</span>
            </div>
          </div>

          <Card className="w-full shadow-lg border-0 bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <Mail className="h-12 w-12 text-red-600" />
                </div>
              </div>
              <CardTitle className="text-xl">Authentication Failed</CardTitle>
              <CardDescription className="text-base">{error}</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <button
                onClick={() => router.push("/")}
                className="text-primary hover:underline font-medium"
              >
                Return to Home
              </button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return null;
}
