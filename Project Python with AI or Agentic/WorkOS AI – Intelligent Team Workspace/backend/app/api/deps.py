from typing import Optional
from uuid import UUID
from fastapi import Depends, Header, Path, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, WorkspaceAccessDeniedError
from app.models.user import User
from app.models.workspace import WorkspaceMember, WorkspaceRoleEnum

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate JWT access token and return active authenticated user."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authentication token is missing.")
    
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type. Access token required.")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Token payload missing subject identity.")
        user_id = UUID(user_id_str)
    except Exception:
        raise AuthenticationError("Invalid or expired authentication token.")

    query = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise AuthenticationError("User associated with this token no longer exists or is inactive.")
    return user


async def get_workspace_id(
    workspace_id: Optional[UUID] = Path(None),
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID"),
) -> UUID:
    """Extract target workspace ID from path parameter or header."""
    if workspace_id:
        return workspace_id
    if x_workspace_id:
        try:
            return UUID(x_workspace_id)
        except ValueError:
            raise WorkspaceAccessDeniedError()
    raise WorkspaceAccessDeniedError()


async def get_current_workspace_member(
    workspace_id: UUID = Depends(get_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceMember:
    """
    CRITICAL TENANT ISOLATION GUARD:
    Verifies that the authenticated user belongs to the requested workspace.
    Denies request with HTTP 403 Forbidden if not a member.
    """
    query = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
    )
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    if not member:
        raise WorkspaceAccessDeniedError(str(workspace_id))
    return member


def require_role(allowed_roles: list[WorkspaceRoleEnum]):
    """RBAC dependency factory that checks if current member role is in allowed_roles."""
    async def role_checker(
        member: WorkspaceMember = Depends(get_current_workspace_member),
    ) -> WorkspaceMember:
        if member.role not in allowed_roles:
            raise WorkspaceAccessDeniedError(str(member.workspace_id))
        return member
    return role_checker


# Convenient RBAC presets
require_workspace_admin = require_role([WorkspaceRoleEnum.OWNER, WorkspaceRoleEnum.ADMIN])
require_workspace_member = require_role([
    WorkspaceRoleEnum.OWNER,
    WorkspaceRoleEnum.ADMIN,
    WorkspaceRoleEnum.MEMBER,
])

