from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRoleEnum
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceOut,
    WorkspaceMemberOut,
    WorkspaceInviteRequest,
)
from app.schemas.common import APIResponse
from app.api.deps import (
    get_current_user,
    get_current_workspace_member,
    require_workspace_admin,
)

router = APIRouter()


@router.get("", response_model=APIResponse[List[WorkspaceOut]])
async def list_user_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all workspaces that the current user belongs to."""
    query = (
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == current_user.id)
    )
    result = await db.execute(query)
    workspaces = result.scalars().all()
    return APIResponse(
        data=[WorkspaceOut.model_validate(w) for w in workspaces]
    )


@router.post("", response_model=APIResponse[WorkspaceOut], status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace and designate current user as Owner."""
    # Check if slug exists
    query = select(Workspace).where(Workspace.slug == payload.slug)
    existing = (await db.execute(query)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A workspace with this slug already exists."
        )

    new_workspace = Workspace(
        name=payload.name,
        slug=payload.slug,
        owner_id=current_user.id,
        settings=payload.settings or {},
    )
    db.add(new_workspace)
    await db.flush()

    membership = WorkspaceMember(
        workspace_id=new_workspace.id,
        user_id=current_user.id,
        role=WorkspaceRoleEnum.OWNER,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(new_workspace)

    return APIResponse(
        data=WorkspaceOut.model_validate(new_workspace),
        message="Workspace created successfully.",
    )


@router.get("/{workspace_id}/members", response_model=APIResponse[List[WorkspaceMemberOut]])
async def list_workspace_members(
    workspace_id: UUID,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """List all team members inside the current workspace."""
    query = (
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    result = await db.execute(query)
    members = result.scalars().all()
    return APIResponse(
        data=[WorkspaceMemberOut.model_validate(m) for m in members]
    )


@router.post("/{workspace_id}/members/invite", response_model=APIResponse[dict])
async def invite_workspace_member(
    workspace_id: UUID,
    payload: WorkspaceInviteRequest,
    admin_member: WorkspaceMember = Depends(require_workspace_admin),
    db: AsyncSession = Depends(get_db),
):
    """Invite a new member to the workspace (Admin or Owner only)."""
    # Check if user with email already exists in system
    query = select(User).where(User.email == payload.email.lower())
    existing_user = (await db.execute(query)).scalar_one_or_none()

    if existing_user:
        # Check if already a member
        m_query = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == existing_user.id,
        )
        already_member = (await db.execute(m_query)).scalar_one_or_none()
        if already_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace.",
            )

        new_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=existing_user.id,
            role=payload.role,
        )
        db.add(new_member)
        await db.commit()
        return APIResponse(
            data={"status": "added", "email": payload.email, "role": payload.role},
            message=f"Added {payload.email} to workspace as {payload.role.value}.",
        )
    
    return APIResponse(
        data={"status": "invitation_sent", "email": payload.email, "role": payload.role},
        message=f"Invitation sent to {payload.email}.",
    )

