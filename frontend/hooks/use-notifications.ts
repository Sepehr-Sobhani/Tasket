import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type NotificationResponse = components["schemas"]["NotificationResponse"];

interface NotificationsData {
  notifications: NotificationResponse[];
  unread_count: number;
}

export function useNotifications() {
  return useQuery<NotificationsData>({
    queryKey: ["notifications"],
    queryFn: () => api.notifications.getAll(),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: (notificationId: number) =>
      api.notifications.markAsRead(notificationId),
    onSuccess: (_, notificationId) => {
      // Optimistically update the cache
      queryClient.setQueryData(
        ["notifications"],
        (old: NotificationsData | undefined) => {
          if (!old) return old;

          return {
            ...old,
            notifications: old.notifications.map((n) =>
              n.id === notificationId ? { ...n, is_read: true } : n
            ),
            unread_count: Math.max(0, old.unread_count - 1),
          };
        }
      );
    },
  });
}

export function useMarkAllNotificationsAsRead() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, void>({
    mutationFn: () => api.notifications.markAllAsRead(),
    onSuccess: () => {
      // Optimistically update the cache
      queryClient.setQueryData(
        ["notifications"],
        (old: NotificationsData | undefined) => {
          if (!old) return old;

          return {
            ...old,
            notifications: old.notifications.map((n) => ({
              ...n,
              is_read: true,
            })),
            unread_count: 0,
          };
        }
      );
    },
  });
}
