from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from app.models.project import ProjectStatusEnum
from app.schemas.user import UserOut


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    target_date: Optional[date] = None
    start_date: Optional[date] = None
    lead_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    target_date: Optional[date] = None
    lead_id: Optional[UUID] = None


class ProjectOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: Optional[str] = None
    status: ProjectStatusEnum
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    lead_id: Optional[UUID] = None
    created_at: datetime
    lead: Optional[UserOut] = None

    class Config:
        from_attributes = True

