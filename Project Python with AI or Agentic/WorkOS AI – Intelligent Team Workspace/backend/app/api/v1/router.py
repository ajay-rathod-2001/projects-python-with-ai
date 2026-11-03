from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    workspaces,
    projects,
    tasks,
    ai,
    meetings,
    analytics,
    integrations,
)

api_router = APIRouter()

# Auth & User Routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Workspace Root Routes
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])

# Nested Workspace Scoped Domain Routes
api_router.include_router(
    projects.router,
    prefix="/workspaces/{workspace_id}/projects",
    tags=["Projects"],
)
api_router.include_router(
    tasks.router,
    prefix="/workspaces/{workspace_id}/tasks",
    tags=["Tasks"],
)
api_router.include_router(
    ai.router,
    prefix="/workspaces/{workspace_id}/ai",
    tags=["AI Agent & RAG"],
)
api_router.include_router(
    meetings.router,
    prefix="/workspaces/{workspace_id}/meetings",
    tags=["Meetings Intelligence"],
)
api_router.include_router(
    analytics.router,
    prefix="/workspaces/{workspace_id}/analytics",
    tags=["Analytics & Risk Engine"],
)
api_router.include_router(
    integrations.router,
    prefix="/workspaces/{workspace_id}/integrations",
    tags=["Integrations"],
)

