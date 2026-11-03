from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.models.audit import ActionStatusEnum


class ProjectPlanRequest(BaseModel):
    brief: str = Field(..., min_length=10, description="Detailed project requirement or brief")
    target_weeks: Optional[int] = Field(default=8, ge=1, le=52)
    project_id: Optional[UUID] = None


class PlannedTask(BaseModel):
    temp_id: str
    title: str
    description: str
    priority: str = "medium"
    estimated_hours: int = 16
    role_suggestion: Optional[str] = "Full Stack Engineer"
    depends_on: List[str] = []


class PlannedMilestone(BaseModel):
    title: str
    week_number: int
    tasks: List[PlannedTask]


class GeneratedPlan(BaseModel):
    project_name: str
    summary: str
    suggested_timeline_weeks: int
    milestones: List[PlannedMilestone]
    identified_risks: List[str]
    suggested_team_roles: List[str]


class StagedPlanResponse(BaseModel):
    action_audit_id: UUID
    status: ActionStatusEnum
    plan: GeneratedPlan
    message: str = "AI Plan generated and staged for review. Approval required before publishing."


class AgentActionApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    project_id: Optional[UUID] = None
    top_k: int = 5


class RAGSourceItem(BaseModel):
    entity_type: str  # document, meeting, task
    entity_id: str
    title: str
    snippet: str
    score: float


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RAGSourceItem]

