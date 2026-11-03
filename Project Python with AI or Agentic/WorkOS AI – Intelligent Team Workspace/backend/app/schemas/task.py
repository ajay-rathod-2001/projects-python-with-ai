from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from app.models.task import TaskStatusEnum, TaskPriorityEnum
from app.schemas.user import UserOut


class TaskDependencyCreate(BaseModel):
    depends_on_task_id: UUID
    dependency_type: str = "blocks"


class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class TaskCommentOut(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    author: Optional[UserOut] = None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.TODO
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None
    estimated_hours: int = 0
    dependency_ids: Optional[List[UUID]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatusEnum


class TaskOut(BaseModel):
    id: UUID
    workspace_id: UUID
    project_id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None
    estimated_hours: int
    actual_hours: int
    created_at: datetime
    assignee: Optional[UserOut] = None
    dependency_ids: List[UUID] = []

    class Config:
        from_attributes = True

