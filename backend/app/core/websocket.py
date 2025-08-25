import json
from datetime import datetime

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Store active connections by user_id
        self.active_connections: dict[int, list[WebSocket]] = {}
        # Store project subscriptions: project_id -> set of user_ids
        self.project_subscriptions: dict[int, set[int]] = {}
        # Store user subscriptions: user_id -> set of project_ids
        self.user_subscriptions: dict[int, set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's WebSocket"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            self.user_subscriptions[user_id] = set()

        self.active_connections[user_id].append(websocket)
        logger.info(
            "User connected",
            user_id=user_id,
            connection_count=len(self.active_connections[user_id]),
        )

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user's WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)

            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_subscriptions:
                    del self.user_subscriptions[user_id]

            logger.info("User disconnected", user_id=user_id)

    def subscribe_to_project(self, user_id: int, project_id: int):
        """Subscribe a user to project updates"""
        if project_id not in self.project_subscriptions:
            self.project_subscriptions[project_id] = set()

        self.project_subscriptions[project_id].add(user_id)

        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()

        self.user_subscriptions[user_id].add(project_id)
        logger.info(
            "User subscribed to project", user_id=user_id, project_id=project_id
        )

    def unsubscribe_from_project(self, user_id: int, project_id: int):
        """Unsubscribe a user from project updates"""
        if project_id in self.project_subscriptions:
            self.project_subscriptions[project_id].discard(user_id)

            if not self.project_subscriptions[project_id]:
                del self.project_subscriptions[project_id]

        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(project_id)

            if not self.user_subscriptions[user_id]:
                del self.user_subscriptions[user_id]

        logger.info(
            "User unsubscribed from project", user_id=user_id, project_id=project_id
        )

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(
                        "Failed to send personal message", user_id=user_id, error=str(e)
                    )

    async def broadcast_to_project(
        self, message: dict, project_id: int, exclude_user: int | None = None
    ):
        """Broadcast a message to all users subscribed to a project"""
        if project_id not in self.project_subscriptions:
            return

        for user_id in self.project_subscriptions[project_id]:
            if user_id != exclude_user:
                await self.send_personal_message(message, user_id)

        logger.info(
            "Broadcasted to project",
            project_id=project_id,
            message_type=message.get("type"),
        )

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

        logger.info("Broadcasted to all users", message_type=message.get("type"))

    def get_connected_users(self) -> list[int]:
        """Get list of connected user IDs"""
        return list(self.active_connections.keys())

    def get_project_subscribers(self, project_id: int) -> set[int]:
        """Get set of user IDs subscribed to a project"""
        return self.project_subscriptions.get(project_id, set())

    def get_user_subscriptions(self, user_id: int) -> set[int]:
        """Get set of project IDs a user is subscribed to"""
        return self.user_subscriptions.get(user_id, set())


# Global connection manager instance
manager = ConnectionManager()


class WebSocketMessage:
    """Helper class for creating WebSocket messages"""

    @staticmethod
    def task_created(task_data: dict, project_id: int):
        return {
            "type": "task_created",
            "project_id": project_id,
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def task_updated(task_data: dict, project_id: int):
        return {
            "type": "task_updated",
            "project_id": project_id,
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def task_deleted(task_id: int, project_id: int):
        return {
            "type": "task_deleted",
            "project_id": project_id,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def task_moved(task_id: int, new_status: str, project_id: int):
        return {
            "type": "task_moved",
            "project_id": project_id,
            "task_id": task_id,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def comment_added(comment_data: dict, project_id: int):
        return {
            "type": "comment_added",
            "project_id": project_id,
            "data": comment_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def user_joined(user_data: dict, project_id: int):
        return {
            "type": "user_joined",
            "project_id": project_id,
            "data": user_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def user_left(user_id: int, project_id: int):
        return {
            "type": "user_left",
            "project_id": project_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def estimation_session_started(session_data: dict, project_id: int):
        return {
            "type": "estimation_session_started",
            "project_id": project_id,
            "data": session_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def estimation_vote(vote_data: dict, project_id: int):
        return {
            "type": "estimation_vote",
            "project_id": project_id,
            "data": vote_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def notification(notification_data: dict):
        return {
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
