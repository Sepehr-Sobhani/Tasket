"use client";

import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent } from "@/components/ui/card";
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
              <p className="text-sm text-muted-foreground">
                {new Date(project.createdAt).toLocaleDateString("en-US", {
                  month: "long",
                  day: "2-digit",
                  year: "numeric",
                })}
              </p>
            </h1>
            <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
              {project.description || "No description provided"}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs px-3 py-1.5 rounded-full font-medium bg-primary/10 text-primary border border-primary/20">
              {project.visibility === "private" ? "Private" : "Public"}
            </span>
          </div>
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
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
