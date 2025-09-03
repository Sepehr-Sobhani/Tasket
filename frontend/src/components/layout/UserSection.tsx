import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Bell, LogOut } from "lucide-react";

interface UserSectionProps {
  user: any;
  isCollapsed: boolean;
  onLogout: () => void;
}

export function UserSection({ user, isCollapsed, onLogout }: UserSectionProps) {
  return (
    <div className="border-t p-3">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="w-full justify-start p-2 h-auto hover:bg-primary/10 transition-colors"
          >
            <Avatar className="h-6 w-6 mr-2">
              <AvatarImage
                src={user?.avatar_url}
                alt={user?.full_name || user?.username}
              />
              <AvatarFallback className="text-xs">
                {(user?.full_name || user?.username || "U")
                  .charAt(0)
                  .toUpperCase()}
              </AvatarFallback>
            </Avatar>
            {!isCollapsed && (
              <div className="flex-1 text-left">
                <p className="text-xs font-medium">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-muted-foreground">
                  {user?.email}
                </p>
              </div>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          className="w-56 p-2 bg-white border border-gray-200 rounded-lg shadow-lg"
          align="end"
          forceMount
        >
          <DropdownMenuLabel className="font-normal p-2">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">
                {user?.full_name || user?.username}
              </p>
              <p className="text-xs leading-none text-muted-foreground">
                {user?.email}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator className="my-1" />
          <DropdownMenuItem
            onClick={() => (window.location.href = "/notifications")}
            className="text-foreground hover:text-primary hover:bg-primary/10 rounded-md p-2 cursor-pointer transition-colors"
          >
            <Bell className="mr-2 h-4 w-4" />
            <span>Notifications</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator className="my-1" />
          <DropdownMenuItem
            onClick={onLogout}
            className="text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md p-2 cursor-pointer transition-colors"
          >
            <LogOut className="mr-2 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
