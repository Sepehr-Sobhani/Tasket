"use client";

import { useParams } from "next/navigation";
import { useProject } from "@/hooks/use-project";
import { Card, CardContent } from "@/components/ui/card";

interface ProjectContentProps {
  user: {
    id: string;
    username: string;
    fullName?: string;
  };
}

export function ProjectContent({}: ProjectContentProps) {
  const params = useParams();
  const projectId = params.id as string;

  const { data: project } = useProject(projectId);

  // Type assertion to help TypeScript understand the data structure
  const projectData = project as any;

  if (!projectData) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-primary">
            {projectData.name}
            <p className="text-sm text-muted-foreground">
              {new Date(projectData.createdAt).toLocaleDateString("en-US", {
                month: "long",
                day: "2-digit",
                year: "numeric",
              })}
            </p>
          </h1>
          <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
            {projectData.description || "No description provided"}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-3 py-1.5 rounded-full font-medium bg-primary/10 text-primary border border-primary/20">
            {projectData.visibility === "private" ? "Private" : "Public"}
          </span>
        </div>
      </div>

      {/* Project Actions */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight text-primary">
          Quick Actions
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 cursor-pointer">
            <CardContent className="p-6">
              <h3 className="font-semibold text-primary mb-2">View Tasks</h3>
              <p className="text-sm text-muted-foreground">
                Manage and track your project tasks
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 cursor-pointer">
            <CardContent className="p-6">
              <h3 className="font-semibold text-primary mb-2">Team Members</h3>
              <p className="text-sm text-muted-foreground">
                Invite and manage team collaboration
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all duration-200 cursor-pointer">
            <CardContent className="p-6">
              <h3 className="font-semibold text-primary mb-2">Settings</h3>
              <p className="text-sm text-muted-foreground">
                Configure project preferences and options
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
