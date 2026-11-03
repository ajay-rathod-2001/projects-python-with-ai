from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from app.models.meeting import ActionItemStatusEnum
from app.schemas.user import UserOut


class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    project_id: Optional[UUID] = None
    raw_transcript: Optional[str] = None


class ActionItemOut(BaseModel):
    id: UUID
    meeting_id: UUID
    action_text: str
    suggested_assignee_id: Optional[UUID] = None
    suggested_due_date: Optional[date] = None
    status: ActionItemStatusEnum
    converted_task_id: Optional[UUID] = None
    suggested_assignee: Optional[UserOut] = None

    class Config:
        from_attributes = True


class MeetingOut(BaseModel):
    id: UUID
    workspace_id: UUID
    project_id: Optional[UUID] = None
    title: str
    summary: Optional[str] = None
    key_decisions: List[str] = []
    created_at: datetime
    action_items: List[ActionItemOut] = []

    class Config:
        from_attributes = True


class MeetingAnalysisResponse(BaseModel):
    summary: str
    decisions: List[str]
    suggested_tasks: List[dict]

