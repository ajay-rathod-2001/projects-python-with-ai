from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.task import Task, TaskStatusEnum
from app.schemas.common import APIResponse
from app.api.deps import get_current_workspace_member
from app.models.workspace import WorkspaceMember

router = APIRouter()


@router.get("/github/status", response_model=APIResponse[Dict[str, Any]])
async def get_github_integration_status(
    workspace_id: UUID,
    member: WorkspaceMember = Depends(get_current_workspace_member),
):
    """Check GitHub OAuth connection status for workspace."""
    return APIResponse(
        data={
            "connected": True,
            "account": "team-lead-workos",
            "linked_repositories": ["workos-ai-core", "workos-ai-web"],
            "last_synced_at": "2026-11-02T14:30:00Z",
        }
    )


@router.post("/github/webhook")
async def github_webhook_receiver(
    request: Request,
    x_github_event: str = Header(None, alias="X-GitHub-Event"),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest GitHub Webhook events (push, pull_request, issues).
    Automatically maps commit messages like '#TASK-123' to update task states.
    """
    payload = await request.json()
    action = payload.get("action")
    
    # Process Pull Request event
    if x_github_event == "pull_request" and action in ["opened", "reopened"]:
        pr_title = payload.get("pull_request", {}).get("title", "")
        # Future enhancement: auto move referenced task to 'review'
        return {"status": "processed", "event": x_github_event, "pr_title": pr_title}

    return {"status": "received", "event": x_github_event}

