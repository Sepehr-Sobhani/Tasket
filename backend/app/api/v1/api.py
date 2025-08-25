from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth_fastapi,
    epics,
    milestones,
    notifications,
    projects,
    tags,
    tasks,
    users,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_fastapi.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(epics.router, prefix="/epics", tags=["epics"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
