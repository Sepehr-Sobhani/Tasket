"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { AuthService } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle, XCircle } from "lucide-react";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [error, setError] = useState<string>("");

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      // Get the authorization code from URL params
      const code = searchParams.get("code");
      const token = searchParams.get("token");
      const error = searchParams.get("error");
      const errorDescription = searchParams.get("error_description");

      if (error) {
        setError(errorDescription || "Authentication failed");
        setStatus("error");
        return;
      }

      if (!token) {
        setError("No authentication token received");
        setStatus("error");
        return;
      }

      // Store the token
      AuthService.setTokenToStorage(token);

      // Refresh user data
      await refreshUser(token);

      // Redirect to dashboard
      setStatus("success");
      setTimeout(() => {
        router.push("/dashboard");
      }, 1500);
    } catch (err) {
      console.error("Auth callback error:", err);
      setError("Authentication failed");
      setStatus("error");
    }
  };

  const handleRetry = () => {
    setStatus("loading");
    setError("");
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="max-w-md w-full space-y-8 text-center">
        {status === "loading" && (
          <div className="space-y-4">
            <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
            <h2 className="text-2xl font-semibold">
              Completing authentication...
            </h2>
            <p className="text-muted-foreground">
              Please wait while we complete your sign-in.
            </p>
          </div>
        )}

        {status === "success" && (
          <div className="space-y-4">
            <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
            <h2 className="text-2xl font-semibold">
              Authentication successful!
            </h2>
          </div>
        )}

        {status === "error" && (
          <div className="space-y-4">
            <XCircle className="h-12 w-12 mx-auto text-red-500" />
            <h2 className="text-2xl font-semibold">Authentication failed</h2>
            <p className="text-muted-foreground">{error}</p>
            <Button onClick={handleRetry} className="mt-4">
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
