"""Pydantic schemas export."""
from app.schemas.common import APIResponse, PaginatedResponse, ErrorResponse, ErrorDetail
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceOut,
    WorkspaceMemberOut,
    WorkspaceInviteRequest,
)
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskOut,
    TaskDependencyCreate,
    TaskCommentCreate,
    TaskCommentOut,
)
from app.schemas.ai import (
    ProjectPlanRequest,
    GeneratedPlan,
    PlannedMilestone,
    PlannedTask,
    StagedPlanResponse,
    AgentActionApproval,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSourceItem,
)
from app.schemas.meeting import (
    MeetingCreate,
    MeetingOut,
    ActionItemOut,
    MeetingAnalysisResponse,
)

__all__ = [
    "APIResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "ErrorDetail",
    "UserRegister",
    "UserLogin",
    "UserOut",
    "TokenResponse",
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceOut",
    "WorkspaceMemberOut",
    "WorkspaceInviteRequest",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectOut",
    "TaskCreate",
    "TaskUpdate",
    "TaskStatusUpdate",
    "TaskOut",
    "TaskDependencyCreate",
    "TaskCommentCreate",
    "TaskCommentOut",
    "ProjectPlanRequest",
    "GeneratedPlan",
    "PlannedMilestone",
    "PlannedTask",
    "StagedPlanResponse",
    "AgentActionApproval",
    "RAGQueryRequest",
    "RAGQueryResponse",
    "RAGSourceItem",
    "MeetingCreate",
    "MeetingOut",
    "ActionItemOut",
    "MeetingAnalysisResponse",
]

