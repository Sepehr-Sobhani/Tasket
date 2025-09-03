import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Target, CheckSquare, Tags } from "lucide-react";

interface SidebarNavigationProps {
  isCollapsed: boolean;
}

export function SidebarNavigation({ isCollapsed }: SidebarNavigationProps) {
  const pathname = usePathname();

  const navigation = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      name: "Epics",
      href: "/epics",
      icon: Target,
    },
    {
      name: "Tasks",
      href: "/tasks",
      icon: CheckSquare,
    },
    {
      name: "Tags",
      href: "/tags",
      icon: Tags,
    },
  ];

  return (
    <nav className="flex-1 space-y-1 p-2">
      {/* Dashboard */}
      <Link
        href="/dashboard"
        className={cn(
          "flex items-center px-2 py-1.5 text-xs font-medium rounded-md transition-all duration-200",
          pathname === "/dashboard"
            ? isCollapsed
              ? "bg-primary text-white shadow-sm w-8 h-8 justify-center"
              : "bg-primary text-white shadow-sm"
            : "text-muted-foreground hover:text-primary hover:bg-primary/10"
        )}
      >
        <LayoutDashboard
          className={cn("h-3.5 w-3.5", !isCollapsed && "mr-2")}
        />
        {!isCollapsed && "Dashboard"}
      </Link>

      {/* Other Navigation Items */}
      {navigation.slice(1).map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center px-2 py-1.5 text-xs font-medium rounded-md transition-all duration-200",
              isActive
                ? isCollapsed
                  ? "bg-primary text-white shadow-sm w-8 h-8 justify-center"
                  : "bg-primary text-white shadow-sm"
                : "text-muted-foreground hover:text-primary hover:bg-primary/10"
            )}
          >
            <item.icon className={cn("h-3.5 w-3.5", !isCollapsed && "mr-2")} />
            {!isCollapsed && item.name}
          </Link>
        );
      })}
    </nav>
  );
}
