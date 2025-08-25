"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { Bell } from "lucide-react";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type NotificationResponse = components["schemas"]["NotificationResponse"];

interface NotificationListProps {
  notifications: NotificationResponse[];
  onNotificationClick: (notificationId: number) => void;
  onClose: () => void;
  showRecentOnly?: boolean;
}

export function NotificationList({
  notifications,
  onNotificationClick,
  onClose,
  showRecentOnly = false,
}: NotificationListProps) {
  const [selectedTab, setSelectedTab] = useState<"all" | "unread">("all");

  const filteredNotifications =
    selectedTab === "unread"
      ? notifications.filter((n) => !n.is_read)
      : notifications;

  // Show only recent notifications in the bell popup
  const displayNotifications = showRecentOnly
    ? filteredNotifications.slice(0, 10)
    : filteredNotifications;

  if (notifications.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p className="text-sm">No notifications yet</p>
        <p className="text-xs">We&apos;ll notify you when something happens</p>
      </div>
    );
  }

  return (
    <div className="max-h-96">
      {/* Tabs - only show in full notifications page */}
      {!showRecentOnly && (
        <div className="flex border-b">
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "flex-1 rounded-none border-b-2",
              selectedTab === "all"
                ? "border-primary text-primary"
                : "border-transparent"
            )}
            onClick={() => setSelectedTab("all")}
          >
            All
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "flex-1 rounded-none border-b-2",
              selectedTab === "unread"
                ? "border-primary text-primary"
                : "border-transparent"
            )}
            onClick={() => setSelectedTab("unread")}
          >
            Unread
          </Button>
        </div>
      )}

      {/* Notifications */}
      <ScrollArea className="h-80">
        <div className="divide-y">
          {displayNotifications.map((notification) => (
            <div
              key={notification.id}
              className={cn(
                "p-4 hover:bg-muted/50 cursor-pointer transition-colors",
                !notification.is_read && "bg-muted/30"
              )}
              onClick={() => onNotificationClick(notification.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-medium truncate">
                      {notification.title}
                    </h4>
                    {!notification.is_read && (
                      <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {notification.message}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(notification.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
