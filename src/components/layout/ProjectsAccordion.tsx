import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { FolderOpen, ChevronDown } from "lucide-react";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type Project = (typeof components)["schemas"]["Project"];

interface ProjectsAccordionProps {
  isCollapsed: boolean;
}

export function ProjectsAccordion({ isCollapsed }: ProjectsAccordionProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(false);
  const [isLoadingProjects, setIsLoadingProjects] = useState(false);
  const pathname = usePathname();

  // Auto-expand projects when on a project details page
  useEffect(() => {
    if (pathname.startsWith("/projects/")) {
      setIsProjectsExpanded(true);
    }
  }, [pathname]);

  // Fetch projects for accordion only when expanded
  useEffect(() => {
    if (!isProjectsExpanded) return; // Don't fetch if accordion is collapsed

    const fetchProjects = async () => {
      setIsLoadingProjects(true);
      try {
        const data = await api.projects.getAll();
        setProjects(data || []);
      } catch (error) {
        console.error("Failed to fetch projects:", error);
      } finally {
        setIsLoadingProjects(false);
      }
    };

    fetchProjects();
  }, [isProjectsExpanded]); // Only fetch when accordion state changes

  return (
    <div className="space-y-1">
      <Button
        variant="ghost"
        className={cn(
          "w-full justify-start px-2 py-1.5 text-xs font-medium rounded-md transition-all duration-200 h-auto",
          pathname.startsWith("/projects/") || pathname === "/projects"
            ? isCollapsed
              ? "bg-primary text-white shadow-sm w-8 h-8 justify-center"
              : "bg-primary text-white shadow-sm"
            : "text-muted-foreground hover:text-primary hover:bg-primary/10"
        )}
        onClick={() =>
          !isCollapsed && setIsProjectsExpanded(!isProjectsExpanded)
        }
      >
        <FolderOpen className={cn("h-3.5 w-3.5", !isCollapsed && "mr-2")} />
        {!isCollapsed && (
          <>
            <span className="flex-1 text-left">Projects</span>
            {projects.length > 0 && (
              <ChevronDown
                className={cn(
                  "h-3 w-3 transition-transform",
                  isProjectsExpanded && "rotate-180"
                )}
              />
            )}
          </>
        )}
      </Button>

      {/* Projects List */}
      {!isCollapsed && projects.length > 0 && isProjectsExpanded && (
        <div className="ml-4 space-y-1">
          {isLoadingProjects ? (
            <div className="px-2 py-1 text-xs text-muted-foreground">
              Loading...
            </div>
          ) : (
            projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className={cn(
                  "flex items-center px-2 py-1 text-xs rounded-md transition-all duration-200",
                  pathname === `/projects/${project.id}`
                    ? "bg-primary/20 text-primary font-medium"
                    : "text-muted-foreground hover:text-primary hover:bg-primary/10"
                )}
              >
                <div className="w-1.5 h-1.5 rounded-full bg-current mr-2" />
                {project.name}
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
}
