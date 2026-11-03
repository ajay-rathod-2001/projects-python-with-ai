from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.project import Project, ProjectStatusEnum
from app.models.workspace import WorkspaceMember
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.common import APIResponse
from app.api.deps import (
    get_current_workspace_member,
    require_workspace_admin,
    require_workspace_member,
)

router = APIRouter()


@router.get("", response_model=APIResponse[List[ProjectOut]])
async def list_projects(
    workspace_id: UUID,
    status: Optional[ProjectStatusEnum] = Query(None),
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """List all projects in the workspace with optional status filter."""
    query = select(Project).where(Project.workspace_id == workspace_id)
    if status:
        query = query.where(Project.status == status)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    return APIResponse(
        data=[ProjectOut.model_validate(p) for p in projects]
    )


@router.post("", response_model=APIResponse[ProjectOut], status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: UUID,
    payload: ProjectCreate,
    member: WorkspaceMember = Depends(require_workspace_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project in the workspace (Admin or Owner only)."""
    new_project = Project(
        workspace_id=workspace_id,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        target_date=payload.target_date,
        lead_id=payload.lead_id or member.user_id,
        status=ProjectStatusEnum.PLANNING,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return APIResponse(
        data=ProjectOut.model_validate(new_project),
        message="Project created successfully.",
    )


@router.get("/{project_id}", response_model=APIResponse[ProjectOut])
async def get_project(
    workspace_id: UUID,
    project_id: UUID,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Get project details."""
    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id,
    )
    project = (await db.execute(query)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    return APIResponse(data=ProjectOut.model_validate(project))


@router.patch("/{project_id}", response_model=APIResponse[ProjectOut])
async def update_project(
    workspace_id: UUID,
    project_id: UUID,
    payload: ProjectUpdate,
    member: WorkspaceMember = Depends(require_workspace_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update project metadata or status."""
    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id,
    )
    project = (await db.execute(query)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return APIResponse(data=ProjectOut.model_validate(project), message="Project updated.")

