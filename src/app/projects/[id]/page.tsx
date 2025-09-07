"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loading } from "@/components/ui/loading";
import { AppLayout } from "@/components/layout/AppLayout";

import { useProject } from "@/hooks/use-project";

export default function ProjectDetailPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  // Use React Query hooks instead of useState and useEffect
  const { data: projectData, isLoading: isLoadingProject } =
    useProject(projectId);

  const project = projectData;

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (isLoading || isLoadingProject) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading size="lg" text="Loading..." />
      </div>
    );
  }

  if (!user || !project) {
    return null;
  }

  return (
    <AppLayout user={user} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-primary">
              {project.name}
            </h1>
            <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
              {project.description || "No description provided"}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs px-3 py-1.5 rounded-full font-medium bg-primary/10 text-primary border border-primary/20">
              {project.visibility === "private" ? "Private" : "Public"}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/dashboard")}
              className="border-primary text-primary hover:bg-primary/10"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-1">
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-primary">
                Project Info
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {project.name}
              </div>
              <p className="text-xs text-muted-foreground">
                Project details and information
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Project Actions */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight text-primary">
            Quick Actions
          </h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">📋</div>
                <h3 className="text-sm font-medium text-primary">
                  Create Task
                </h3>
                <p className="text-xs text-muted-foreground">Add new task</p>
              </CardContent>
            </Card>

            <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">👥</div>
                <h3 className="text-sm font-medium text-primary">
                  Invite Team
                </h3>
                <p className="text-xs text-muted-foreground">Add members</p>
              </CardContent>
            </Card>

            <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">📊</div>
                <h3 className="text-sm font-medium text-primary">
                  View Reports
                </h3>
                <p className="text-xs text-muted-foreground">
                  Project analytics
                </p>
              </CardContent>
            </Card>

            <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">⚙️</div>
                <h3 className="text-sm font-medium text-primary">Settings</h3>
                <p className="text-xs text-muted-foreground">
                  Configure project
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Project Details */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight text-primary">
            Project Details
          </h2>
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-primary">Description</h3>
                  <p className="text-sm text-muted-foreground">
                    {project.description || "No description provided"}
                  </p>
                </div>
                <div>
                  <h3 className="font-medium text-primary">Visibility</h3>
                  <p className="text-sm text-muted-foreground capitalize">
                    {project.visibility}
                  </p>
                </div>
                <div>
                  <h3 className="font-medium text-primary">Created</h3>
                  <p className="text-sm text-muted-foreground">
                    {new Date(project.created_at).toLocaleDateString("en-US", {
                      month: "long",
                      day: "2-digit",
                      year: "numeric",
                    })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
