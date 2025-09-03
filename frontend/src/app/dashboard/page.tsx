"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useCreateProject } from "@/hooks/use-project-mutations";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loading } from "@/components/ui/loading";
import { AppLayout } from "@/components/layout/AppLayout";
import { CreateProjectForm } from "@/components/project/CreateProjectForm";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Plus } from "lucide-react";

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();
  const [showCreateProject, setShowCreateProject] = useState(false);

  const { mutateAsync: createProject, isPending: isCreating } =
    useCreateProject();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const handleCreateProject = async (projectData: {
    name: string;
    description: string;
    visibility: string;
  }) => {
    try {
      const newProject = await createProject(projectData);
      setShowCreateProject(false);
      // Redirect to the new project
      router.push(`/projects/${newProject.id}`);
    } catch (error) {
      console.error("Failed to create project:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loading size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <AppLayout user={user} onLogout={handleLogout}>
      <div className="space-y-8">
        {/* Welcome Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              Welcome back, {user.full_name || user.username}!
            </h1>
          </div>
        </div>

        {/* Getting Started */}
        <div className="space-y-4">
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader>
              <CardTitle className="text-primary">Welcome to Tasket!</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                You're all set up! Here are some things you can do to get
                started:
              </p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Badge
                    variant="outline"
                    className="border-primary text-primary"
                  >
                    1
                  </Badge>
                  <span className="text-sm">
                    Create your first project to organize your work
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge
                    variant="outline"
                    className="border-primary text-primary"
                  >
                    2
                  </Badge>
                  <span className="text-sm">
                    Invite team members to collaborate
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge
                    variant="outline"
                    className="border-primary text-primary"
                  >
                    3
                  </Badge>
                  <span className="text-sm">
                    Start creating tasks and tracking progress
                  </span>
                </div>
              </div>
              <Button
                onClick={() => setShowCreateProject(true)}
                className="bg-primary hover:bg-primary/90 text-white mt-4"
              >
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Project
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Project Dialog */}
      <Dialog open={showCreateProject} onOpenChange={setShowCreateProject}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
          </DialogHeader>
          <CreateProjectForm
            onSubmit={handleCreateProject}
            onCancel={() => setShowCreateProject(false)}
            isLoading={isCreating}
          />
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
