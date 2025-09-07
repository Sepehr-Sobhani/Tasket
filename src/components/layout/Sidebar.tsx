"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { SidebarHeader } from "./SidebarHeader";
import { SidebarNavigation } from "./SidebarNavigation";
import { UserSection } from "./UserSection";

interface SidebarProps {
  user: any;
}

export function Sidebar({ user }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div
        className={cn(
          "flex flex-col border-r bg-background transition-all duration-300",
          isCollapsed ? "w-16" : "w-64"
        )}
      >
        <SidebarHeader
          isCollapsed={isCollapsed}
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        />

        <div className="flex-1 space-y-1 p-2">
          <SidebarNavigation isCollapsed={isCollapsed} />
        </div>

        <UserSection user={user} isCollapsed={isCollapsed} />
      </div>
    </div>
  );
}
