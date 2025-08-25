"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
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
import { CreateEpicForm } from "@/components/epic/CreateEpicForm";
import { CreateTaskForm } from "@/components/task/CreateTaskForm";
import { TagManager } from "@/components/tag/TagManager";
import { AppLayout } from "@/components/layout/AppLayout";
import { Plus, Target, CheckSquare, Tags, ArrowLeft } from "lucide-react";
import { useProject, useProjectEpics, useProjectTasks, useProjectTags, useUsers } from "@/hooks/use-project";
import { useCreateEpic, useCreateTask } from "@/hooks/use-project-mutations";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type User = components["schemas"]["User"];

export default function ProjectDetailPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const projectId = parseInt(params.id as string);

  // Use React Query hooks instead of useState and useEffect
  const { data: projectData, isLoading: isLoadingProject } = useProject(projectId);
  const { data: epicsData, isLoading: isLoadingEpics } = useProjectEpics(projectId);
  const { data: tasksData, isLoading: isLoadingTasks } = useProjectTasks(projectId);
  const { data: tagsData, isLoading: isLoadingTags } = useProjectTags(projectId);
  const { data: usersData, isLoading: isLoadingUsers } = useUsers();

  const project = projectData;
  const epics = epicsData?.epics || [];
  const tasks = tasksData?.tasks || [];
  const tags = tagsData?.tags || [];
  const users = usersData?.users || [];

  const [isCreateEpicModalOpen, setIsCreateEpicModalOpen] = useState(false);
  const [isCreateTaskModalOpen, setIsCreateTaskModalOpen] = useState(false);
  
  // Use mutation hooks
  const createEpicMutation = useCreateEpic();
  const createTaskMutation = useCreateTask();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const handleCreateEpic = () => {
    setIsCreateEpicModalOpen(true);
  };

  const handleCreateEpicSubmit = async (data: {
    title: string;
    description: string;
  }) => {
    try {
      await createEpicMutation.mutateAsync({
        ...data,
        project_id: projectId,
      });
      setIsCreateEpicModalOpen(false);
    } catch (error) {
      console.error("Error creating epic:", error);
    }
  };

  const handleCreateTask = () => {
    setIsCreateTaskModalOpen(true);
  };

  const handleCreateTaskSubmit = async (data: {
    title: string;
    description: string;
    priority: string;
    assignee_id?: number;
    epic_id?: number;
  }) => {
    try {
      await createTaskMutation.mutateAsync({
        ...data,
        project_id: projectId,
      });
      setIsCreateTaskModalOpen(false);
    } catch (error) {
      console.error("Error creating task:", error);
    }
  };

  const handleTagCreated = (newTag: any) => {
    // This will be handled by React Query's cache invalidation
    window.location.reload(); // Temporary solution
  };

  const handleTagDeleted = (tagId: number) => {
    // This will be handled by React Query's cache invalidation
    window.location.reload(); // Temporary solution
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
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-primary">
                Tasks
              </CardTitle>
              <CheckSquare className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {tasks.length}
              </div>
              <p className="text-xs text-muted-foreground">
                Total tasks in project
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-primary">
                Epics
              </CardTitle>
              <Target className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {epics.length}
              </div>
              <p className="text-xs text-muted-foreground">
                Total epics in project
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-primary">
                Tags
              </CardTitle>
              <Tags className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {tags.length}
              </div>
              <p className="text-xs text-muted-foreground">Available tags</p>
            </CardContent>
          </Card>
        </div>

        {/* Tasks Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight text-primary">
              Tasks
            </h2>
            <Button
              onClick={handleCreateTask}
              size="sm"
              className="bg-primary hover:bg-primary/90 text-white shadow-sm"
            >
              <Plus className="mr-2 h-4 w-4" />
              New Task
            </Button>
          </div>

          {isLoadingTasks ? (
            <div className="flex items-center justify-center py-12">
              <Loading size="md" text="Loading tasks..." />
            </div>
          ) : tasks.length === 0 ? (
            <Card className="border-dashed border-primary/30 bg-primary/5">
              <CardContent className="p-12 text-center">
                <CheckSquare className="w-16 h-16 mx-auto mb-6 text-primary" />
                <h3 className="text-xl font-semibold mb-3 text-primary">
                  No tasks yet
                </h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                  Create your first task to get started with work.
                </p>
                <Button
                  onClick={handleCreateTask}
                  size="sm"
                  className="bg-primary hover:bg-primary/90 text-white"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Task
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {tasks.slice(0, 6).map((task: any) => (
                <Card
                  key={task.id}
                  className="hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer border-primary/10 hover:border-primary/30"
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center text-primary">
                      <CheckSquare className="h-4 w-4 mr-2 text-primary" />
                      {task.title}
                    </CardTitle>
                    <CardDescription className="text-sm">
                      {task.description || "No description"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            task.priority === "urgent"
                              ? "bg-red-100 text-red-800"
                              : task.priority === "high"
                                ? "bg-orange-100 text-orange-800"
                                : task.priority === "medium"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-green-100 text-green-800"
                          }`}
                        >
                          {task.priority}
                        </span>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            task.status === "draft"
                              ? "bg-gray-100 text-gray-800"
                              : task.status === "in_progress"
                                ? "bg-blue-100 text-blue-800"
                                : task.status === "review"
                                  ? "bg-purple-100 text-purple-800"
                                  : "bg-green-100 text-green-800"
                          }`}
                        >
                          {task.status}
                        </span>
                      </div>
                      <span>
                        {new Date(task.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "2-digit",
                          year: "numeric",
                        })}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Epics Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight text-primary">
              Epics
            </h2>
            <Button
              onClick={handleCreateEpic}
              size="sm"
              variant="outline"
              className="border-primary/30 text-primary hover:bg-primary/5"
            >
              <Plus className="mr-2 h-4 w-4" />
              New Epic
            </Button>
          </div>

          {isLoadingEpics ? (
            <div className="flex items-center justify-center py-12">
              <Loading size="md" text="Loading epics..." />
            </div>
          ) : epics.length === 0 ? (
            <Card className="border-dashed border-primary/30 bg-primary/5">
              <CardContent className="p-12 text-center">
                <Target className="w-16 h-16 mx-auto mb-6 text-primary" />
                <h3 className="text-xl font-semibold mb-3 text-primary">
                  No epics yet
                </h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                  Create your first epic to organize your project work.
                </p>
                <Button
                  onClick={handleCreateEpic}
                  size="sm"
                  variant="outline"
                  className="border-primary/30 text-primary hover:bg-primary/5"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Epic
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {epics.slice(0, 6).map((epic: any) => (
                <Card
                  key={epic.id}
                  className="hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer border-primary/10 hover:border-primary/30"
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center text-primary">
                      <Target className="h-4 w-4 mr-2 text-primary" />
                      {epic.title}
                    </CardTitle>
                    <CardDescription className="text-sm">
                      {epic.description || "No description"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="text-xs text-muted-foreground">
                      Created{" "}
                      {new Date(epic.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "2-digit",
                        year: "numeric",
                      })}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Tags Section */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight text-primary">
            Project Tags
          </h2>
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="p-6">
              {isLoadingTags ? (
                <div className="flex items-center justify-center py-8">
                  <Loading size="md" text="Loading tags..." />
                </div>
              ) : (
                <TagManager
                  projectId={projectId}
                  tags={tags}
                  onTagCreated={handleTagCreated}
                  onTagDeleted={handleTagDeleted}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Create Epic Modal */}
        <Modal
          isOpen={isCreateEpicModalOpen}
          onClose={() => setIsCreateEpicModalOpen(false)}
          title="Create New Epic"
        >
          <CreateEpicForm
            projectId={projectId}
            onSubmit={handleCreateEpicSubmit}
            onCancel={() => setIsCreateEpicModalOpen(false)}
            isLoading={createEpicMutation.isPending}
          />
        </Modal>

        {/* Create Task Modal */}
        <Modal
          isOpen={isCreateTaskModalOpen}
          onClose={() => setIsCreateTaskModalOpen(false)}
          title="Create New Task"
          size="lg"
        >
          <CreateTaskForm
            projectId={projectId}
            epics={epics}
            users={users}
            onSubmit={handleCreateTaskSubmit}
            onCancel={() => setIsCreateTaskModalOpen(false)}
            isLoading={createTaskMutation.isPending}
          />
        </Modal>
      </div>
    </AppLayout>
  );
}
