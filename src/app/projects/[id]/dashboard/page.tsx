"use client";

import { useEffect } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useProject } from "@/hooks/use-project";
import { Button } from "@/components/ui/button";
import { Loading } from "@/components/ui/loading";
import { AppLayout } from "@/components/layout/AppLayout";
import { LogOut } from "lucide-react";

export default function ProjectDashboardPage() {
  const { user, logout, isLoading, refreshUser } = useAuth();
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = params.id as string;

  const { data: project, isLoading: projectLoading } = useProject(projectId);

  // Handle token from URL (OAuth callback)
  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      // Store the token and refresh user data
      localStorage.setItem("auth_token", token);
      refreshUser(token);

      // Remove token from URL
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete("token");
      window.history.replaceState({}, "", newUrl.toString());
    }
  }, [searchParams, refreshUser]);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (isLoading || projectLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading size="lg" text="Loading project..." />
      </div>
    );
  }

  if (!user || !project) {
    return null;
  }

  return (
    <AppLayout user={user} onLogout={handleLogout}>
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight text-primary">
              Dashboard for Project {project.id}
            </h1>
            <p className="text-lg text-muted-foreground">
              Welcome to your project dashboard!
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              <strong>Project Name:</strong> {project.name}
            </p>
            <p className="text-sm text-muted-foreground">
              <strong>Description:</strong>{" "}
              {project.description || "No description"}
            </p>
            <p className="text-sm text-muted-foreground">
              <strong>Visibility:</strong> {project.visibility}
            </p>
            {project.isDefault && (
              <p className="text-sm text-green-600 font-medium">
                ✓ This is your default project
              </p>
            )}
          </div>

          <Button
            onClick={handleLogout}
            variant="outline"
            className="border-primary text-primary hover:bg-primary/10"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}
