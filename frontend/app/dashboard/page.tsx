"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loading } from "@/components/ui/loading";
import { Modal } from "@/components/ui/modal";
import { CreateProjectForm } from "@/components/project/CreateProjectForm";
import { AppLayout } from "@/components/layout/AppLayout";
import { Plus, FolderOpen, Users, CheckSquare, TrendingUp } from "lucide-react";
import { useDashboardStats, useProjects } from "@/hooks/use-dashboard";
import { useCreateProject } from "@/hooks/use-project-mutations";

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  // Use React Query hooks instead of useState and useEffect
  const { data: statsData, isLoading: isLoadingStats } = useDashboardStats();
  const { data: projectsData, isLoading: isLoadingProjects } = useProjects();
  const createProjectMutation = useCreateProject();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const dashboardStats = statsData;
  const projects = projectsData?.projects || [];

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const handleCreateProject = () => {
    setIsCreateModalOpen(true);
  };

  const handleCreateProjectSubmit = async (data: {
    name: string;
    description: string;
    visibility: string;
  }) => {
    try {
      console.log("Creating project with data:", data);
      const result = await createProjectMutation.mutateAsync(data);
      console.log("Project created successfully:", result);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading size="lg" text="Loading..." />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <AppLayout user={user} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-primary">
              Dashboard
            </h1>
            <p className="text-xs text-muted-foreground mt-1">
              Welcome back! Here&apos;s an overview of your projects.
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Card className="border-primary bg-primary/10 hover:bg-primary/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium text-primary">
                Total Projects
              </CardTitle>
              <FolderOpen className="h-3.5 w-3.5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-primary">
                {isLoadingStats ? "..." : dashboardStats?.total_projects || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                +{dashboardStats?.total_projects || 0 > 0 ? "1" : "0"} from last
                month
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary bg-primary/10 hover:bg-primary/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium text-primary">
                Team Members
              </CardTitle>
              <Users className="h-3.5 w-3.5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-primary">
                {isLoadingStats
                  ? "..."
                  : dashboardStats?.unique_team_members || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Unique across all projects
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary bg-primary/10 hover:bg-primary/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium text-primary">
                Total Tasks
              </CardTitle>
              <CheckSquare className="h-3.5 w-3.5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-primary">
                {isLoadingStats ? "..." : dashboardStats?.total_tasks || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary bg-primary/10 hover:bg-primary/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium text-primary">
                Active Projects
              </CardTitle>
              <TrendingUp className="h-3.5 w-3.5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-primary">
                {isLoadingStats ? "..." : dashboardStats?.active_projects || 0}
              </div>
              <p className="text-xs text-muted-foreground">With active work</p>
            </CardContent>
          </Card>
        </div>

        {/* Projects Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold tracking-tight text-primary">
              Recent Projects
            </h2>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCreateProject}
              className="border-primary text-primary hover:bg-primary/10"
            >
              <Plus className="mr-2 h-3 w-3" />
              Add Project
            </Button>
          </div>

          {isLoadingProjects ? (
            <div className="flex items-center justify-center py-12">
              <Loading size="md" text="Loading projects..." />
            </div>
          ) : projects.length === 0 ? (
            <Card className="border-dashed border-primary">
              <CardContent className="p-6 text-center">
                <FolderOpen className="w-10 h-10 mx-auto mb-3 text-primary" />
                <h3 className="text-base font-semibold mb-2 text-primary">
                  No projects yet
                </h3>
                <p className="text-xs text-muted-foreground mb-4">
                  Create your first project to get started with task management.
                </p>
                <Button
                  onClick={handleCreateProject}
                  size="sm"
                  className="bg-primary hover:bg-primary/90 text-white"
                >
                  <Plus className="mr-2 h-3 w-3" />
                  Create Your First Project
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {projects.slice(0, 6).map((project: any) => (
                <Card
                  key={project.id}
                  className="hover:shadow-md hover:bg-primary/10 transition-all duration-200 cursor-pointer border-primary/20 hover:border-primary/40"
                  onClick={() => router.push(`/projects/${project.id}`)}
                >
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center text-primary">
                      <FolderOpen className="h-3.5 w-3.5 mr-2 text-primary" />
                      {project.name}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {project.description || "No description"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center">
                          <Users className="h-3 w-3 mr-1" />
                          {project.member_count}
                        </span>
                        <span className="text-xs">
                          {new Date(project.created_at).toLocaleDateString(
                            "en-US",
                            {
                              month: "short",
                              day: "2-digit",
                              year: "numeric",
                            }
                          )}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Create Project Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Create New Project"
        >
          <CreateProjectForm
            onSubmit={handleCreateProjectSubmit}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={createProjectMutation.isPending}
          />
        </Modal>
      </div>
    </AppLayout>
  );
}
