from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from app.models.workspace import WorkspaceRoleEnum
from app.schemas.user import UserOut


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceMemberOut(BaseModel):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    role: WorkspaceRoleEnum
    joined_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


class WorkspaceOut(BaseModel):
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    settings: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceInviteRequest(BaseModel):
    email: EmailStr
    role: WorkspaceRoleEnum = WorkspaceRoleEnum.MEMBER

