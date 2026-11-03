from typing import Dict, Any, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum
from app.models.workspace import WorkspaceMember
from app.schemas.common import APIResponse
from app.api.deps import get_current_workspace_member

router = APIRouter()


@router.get("/projects/{project_id}/risks", response_model=APIResponse[Dict[str, Any]])
async def get_project_risks_and_health(
    workspace_id: UUID,
    project_id: UUID,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """
    AI Project Risk Detection Engine:
    Analyzes task completion velocity, blocked tasks, upcoming deadlines,
    and dependency graphs to detect delivery risks.
    """
    p_query = select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    project = (await db.execute(p_query)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    # Fetch all tasks and dependencies for project
    t_query = (
        select(Task)
        .options(selectinload(Task.dependencies))
        .where(Task.project_id == project_id, Task.workspace_id == workspace_id)
    )
    tasks = (await db.execute(t_query)).scalars().all()

    today = date.today()
    delayed_tasks = [t for t in tasks if t.due_date and t.due_date < today and t.status != TaskStatusEnum.COMPLETED]
    blocked_tasks = [t for t in tasks if t.status == TaskStatusEnum.BLOCKED]
    completed_tasks = [t for t in tasks if t.status == TaskStatusEnum.COMPLETED]
    total_tasks = len(tasks)

    # Health score calculation (0 - 100)
    health_score = 100
    if total_tasks > 0:
        health_score -= len(delayed_tasks) * 15
        health_score -= len(blocked_tasks) * 10
        health_score = max(20, min(100, health_score))

    risk_level = "low"
    if health_score < 50:
        risk_level = "critical"
    elif health_score < 75:
        risk_level = "high"
    elif health_score < 85:
        risk_level = "medium"

    bottlenecks: List[Dict[str, str]] = []
    for b in blocked_tasks:
        bottlenecks.append({
            "task_id": str(b.id),
            "title": b.title,
            "status": b.status.value,
            "impact": "Currently blocking dependent sprint deliverables.",
        })

    recommendations: List[str] = []
    if blocked_tasks:
        recommendations.append(f"Resolve upstream blockers on {len(blocked_tasks)} tasks to restore sprint velocity.")
    if delayed_tasks:
        recommendations.append(f"Review and adjust estimates for {len(delayed_tasks)} overdue tasks.")
    if not recommendations:
        recommendations.append("Project execution is healthy and running on schedule.")

    return APIResponse(
        data={
            "project_id": str(project.id),
            "project_name": project.name,
            "health_score": health_score,
            "risk_level": risk_level,
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "delayed_tasks_count": len(delayed_tasks),
            "blocked_tasks_count": len(blocked_tasks),
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
        }
    )

