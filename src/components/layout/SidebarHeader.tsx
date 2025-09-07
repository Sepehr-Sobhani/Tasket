import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/ui/theme-toggle";

interface SidebarHeaderProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function SidebarHeader({
  isCollapsed,
  onToggleCollapse,
}: SidebarHeaderProps) {
  return (
    <div className="flex h-14 items-center justify-between px-3 border-b">
      {!isCollapsed && (
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 bg-primary rounded-md flex items-center justify-center">
            <span className="text-white font-bold text-xs">F</span>
          </div>
          <span className="text-sm font-semibold text-primary">Flowmate</span>
        </div>
      )}
      <div className="flex items-center space-x-1">
        {!isCollapsed && <ThemeToggle />}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="h-7 w-7 p-0"
        >
          {isCollapsed ? (
            <Menu className="h-3 w-3" />
          ) : (
            <X className="h-3 w-3" />
          )}
        </Button>
      </div>
    </div>
  );
}
