from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.database.redis import RedisService
from app.models.task import (
    Task,
    TaskStatusEnum,
    TaskPriorityEnum,
    TaskDependency,
    TaskComment,
)
from app.models.project import Project
from app.models.workspace import WorkspaceMember
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskOut,
    TaskDependencyCreate,
    TaskCommentCreate,
    TaskCommentOut,
)
from app.schemas.common import APIResponse
from app.api.deps import (
    get_current_workspace_member,
    require_workspace_member,
)

router = APIRouter()


@router.get("", response_model=APIResponse[List[TaskOut]])
async def list_tasks(
    workspace_id: UUID,
    project_id: Optional[UUID] = Query(None),
    status: Optional[TaskStatusEnum] = Query(None),
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """List tasks in workspace with optional project and status filters."""
    query = (
        select(Task)
        .options(selectinload(Task.assignee), selectinload(Task.dependencies))
        .where(Task.workspace_id == workspace_id)
    )
    if project_id:
        query = query.where(Task.project_id == project_id)
    if status:
        query = query.where(Task.status == status)

    result = await db.execute(query)
    tasks = result.scalars().all()

    response_items = []
    for t in tasks:
        item = TaskOut.model_validate(t)
        item.dependency_ids = [d.depends_on_task_id for d in t.dependencies]
        response_items.append(item)

    return APIResponse(data=response_items)


@router.post("", response_model=APIResponse[TaskOut], status_code=status.HTTP_201_CREATED)
async def create_task(
    workspace_id: UUID,
    project_id: UUID,
    payload: TaskCreate,
    member: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task within a project."""
    # Verify project belongs to workspace
    p_query = select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    project = (await db.execute(p_query)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found in workspace.")

    new_task = Task(
        workspace_id=workspace_id,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
        estimated_hours=payload.estimated_hours,
    )
    db.add(new_task)
    await db.flush()

    # Add dependencies if provided
    if payload.dependency_ids:
        for dep_id in payload.dependency_ids:
            dep = TaskDependency(
                task_id=new_task.id,
                depends_on_task_id=dep_id,
            )
            db.add(dep)

    await db.commit()
    await db.refresh(new_task)

    # Publish real-time event to workspace channel
    await RedisService.publish_workspace_event(
        workspace_id=str(workspace_id),
        event_type="task.created",
        data={"task_id": str(new_task.id), "title": new_task.title, "status": new_task.status.value},
    )

    out = TaskOut.model_validate(new_task)
    out.dependency_ids = payload.dependency_ids or []
    return APIResponse(data=out, message="Task created successfully.")


@router.patch("/{task_id}/status", response_model=APIResponse[TaskOut])
async def update_task_status(
    workspace_id: UUID,
    task_id: UUID,
    payload: TaskStatusUpdate,
    member: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Update task status (used by Kanban drag-and-drop) and broadcast via WebSocket."""
    query = (
        select(Task)
        .options(selectinload(Task.assignee), selectinload(Task.dependencies))
        .where(Task.id == task_id, Task.workspace_id == workspace_id)
    )
    task = (await db.execute(query)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    old_status = task.status
    task.status = payload.status
    await db.commit()
    await db.refresh(task)

    # Broadcast Kanban move event across all connected team sessions
    await RedisService.publish_workspace_event(
        workspace_id=str(workspace_id),
        event_type="task.moved",
        data={
            "task_id": str(task.id),
            "old_status": old_status.value,
            "new_status": task.status.value,
            "updated_by": str(member.user_id),
        },
    )

    out = TaskOut.model_validate(task)
    out.dependency_ids = [d.depends_on_task_id for d in task.dependencies]
    return APIResponse(data=out, message=f"Task moved to {payload.status.value}.")


@router.post("/{task_id}/comments", response_model=APIResponse[TaskCommentOut], status_code=status.HTTP_201_CREATED)
async def add_task_comment(
    workspace_id: UUID,
    task_id: UUID,
    payload: TaskCommentCreate,
    member: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Add a discussion comment to a task."""
    query = select(Task).where(Task.id == task_id, Task.workspace_id == workspace_id)
    task = (await db.execute(query)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    comment = TaskComment(
        task_id=task.id,
        author_id=member.user_id,
        content=payload.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # Real-time comment event
    await RedisService.publish_workspace_event(
        workspace_id=str(workspace_id),
        event_type="task.comment_added",
        data={"task_id": str(task.id), "comment_id": str(comment.id)},
    )

    return APIResponse(data=TaskCommentOut.model_validate(comment), message="Comment posted.")

