import json

import structlog
from app.core.database import get_async_session
from app.core.websocket import manager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

logger = structlog.get_logger()
router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


async def handle_websocket_message(
    websocket: WebSocket, user_id: int, message: dict, db: Session
):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")

    try:
        if message_type == "subscribe_project":
            project_id = message.get("project_id")
            if project_id:
                manager.subscribe_to_project(user_id, project_id)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscribed",
                            "project_id": project_id,
                            "message": f"Subscribed to project {project_id}",
                        }
                    )
                )

        elif message_type == "unsubscribe_project":
            project_id = message.get("project_id")
            if project_id:
                manager.unsubscribe_from_project(user_id, project_id)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "unsubscribed",
                            "project_id": project_id,
                            "message": f"Unsubscribed from project {project_id}",
                        }
                    )
                )

        elif message_type == "ping":
            await websocket.send_text(
                json.dumps({"type": "pong", "timestamp": message.get("timestamp")})
            )

        elif message_type == "task_move":
            # Handle task drag-and-drop
            task_id = message.get("task_id")
            new_status = message.get("new_status")
            project_id = message.get("project_id")

            if all([task_id, new_status, project_id]):
                # Broadcast task move to project subscribers
                move_message = WebSocketMessage.task_moved(
                    task_id, new_status, project_id
                )
                await manager.broadcast_to_project(
                    move_message, project_id, exclude_user=user_id
                )

        elif message_type == "estimation_vote":
            # Handle estimation voting
            task_id = message.get("task_id")
            vote_value = message.get("vote_value")
            project_id = message.get("project_id")

            if all([task_id, vote_value, project_id]):
                vote_message = WebSocketMessage.estimation_vote(
                    {"task_id": task_id, "vote_value": vote_value, "user_id": user_id},
                    project_id,
                )
                await manager.broadcast_to_project(vote_message, project_id)

        else:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                )
            )

    except Exception as e:
        logger.error(
            "Error handling WebSocket message",
            user_id=user_id,
            message_type=message_type,
            error=str(e),
        )
        await websocket.send_text(
            json.dumps({"type": "error", "message": "Internal server error"})
        )
