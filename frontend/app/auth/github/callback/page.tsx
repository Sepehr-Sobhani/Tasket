"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { AuthService } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loading } from "@/components/ui/loading";
import { CheckCircle, XCircle, Github, Shield, Users, Zap } from "lucide-react";

export default function GitHubCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [error, setError] = useState<string>("");

  useEffect(() => {
    handleGitHubCallback();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGitHubCallback = async () => {
    try {
      const token = searchParams.get("token");
      const error = searchParams.get("error");
      const errorDescription = searchParams.get("error_description");

      if (error) {
        setError(
          errorDescription || "GitHub authentication was cancelled or failed"
        );
        setStatus("error");
        return;
      }

      if (!token) {
        setError("No authentication token received");
        setStatus("error");
        return;
      }

      // Store token
      AuthService.setTokenToStorage(token);

      // Refresh user data
      await refreshUser(token);

      setStatus("success");

      // Redirect to dashboard after a short delay
      setTimeout(() => {
        router.push("/dashboard");
      }, 2000);
    } catch (err) {
      console.error("GitHub callback error:", err);
      setError(err instanceof Error ? err.message : "Authentication failed");
      setStatus("error");
    }
  };

  const handleRetry = () => {
    setStatus("loading");
    setError("");
    handleGitHubCallback();
  };

  const handleGoHome = () => {
    router.push("/");
  };

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
          <CardHeader className="text-center pb-4">
            <div className="flex justify-center mb-4">
              {status === "loading" && (
                <div className="relative">
                  <Loading size="lg" />
                  <Github className="absolute inset-0 m-auto h-6 w-6 text-muted-foreground" />
                </div>
              )}
              {status === "success" && (
                <div className="relative">
                  <CheckCircle className="h-12 w-12 text-green-600" />
                  <Github className="absolute -bottom-1 -right-1 h-5 w-5 text-muted-foreground bg-background rounded-full p-0.5" />
                </div>
              )}
              {status === "error" && (
                <div className="relative">
                  <XCircle className="h-12 w-12 text-red-600" />
                  <Github className="absolute -bottom-1 -right-1 h-5 w-5 text-muted-foreground bg-background rounded-full p-0.5" />
                </div>
              )}
            </div>
            <CardTitle className="text-xl">
              {status === "loading" && "Connecting to GitHub..."}
              {status === "success" && "Successfully Connected!"}
              {status === "error" && "Connection Failed"}
            </CardTitle>
            <CardDescription className="text-base">
              {status === "loading" &&
                "Please wait while we complete your GitHub authentication"}
              {status === "success" &&
                "You have been successfully authenticated with GitHub. Redirecting to dashboard..."}
              {status === "error" && error}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {status === "error" && (
              <div className="space-y-3">
                <Button onClick={handleRetry} className="w-full">
                  Try Again
                </Button>
                <Button
                  onClick={handleGoHome}
                  variant="outline"
                  className="w-full"
                >
                  Go Home
                </Button>
              </div>
            )}
            {status === "success" && (
              <div className="text-center space-y-4">
                <div className="text-sm text-muted-foreground">
                  Redirecting to dashboard...
                </div>
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
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
