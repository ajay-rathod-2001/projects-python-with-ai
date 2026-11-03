from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
import uuid


class WorkOSBaseException(Exception):
    """Base exception for all WorkOS domain exceptions."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(WorkOSBaseException):
    def __init__(self, message: str = "Invalid credentials or expired token"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class WorkspaceAccessDeniedError(WorkOSBaseException):
    def __init__(self, workspace_id: Optional[str] = None):
        super().__init__(
            message="User does not have access to this workspace or lacks required permissions.",
            code="WORKSPACE_ACCESS_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"workspace_id": workspace_id} if workspace_id else {},
        )


class WorkspaceNotFoundError(WorkOSBaseException):
    def __init__(self, workspace_id: str):
        super().__init__(
            message=f"Workspace '{workspace_id}' was not found.",
            code="WORKSPACE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"workspace_id": workspace_id},
        )


class EntityNotFoundError(WorkOSBaseException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' not found.",
            code=f"{entity_name.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "id": entity_id},
        )


class TaskDependencyCycleError(WorkOSBaseException):
    def __init__(self, task_id: str, depends_on_id: str):
        super().__init__(
            message="Circular task dependency detected. Task cannot directly or indirectly depend on itself.",
            code="CIRCULAR_DEPENDENCY_DETECTED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"task_id": task_id, "depends_on_id": depends_on_id},
        )


class AgentApprovalRequiredError(WorkOSBaseException):
    def __init__(self, action_id: str):
        super().__init__(
            message="This action mutates workspace data and requires explicit human approval.",
            code="HUMAN_APPROVAL_REQUIRED",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"action_id": action_id},
        )


async def workos_exception_handler(request: Request, exc: WorkOSBaseException) -> JSONResponse:
    """Standardized JSON response for all custom domain exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Central fallback handler for unhandled errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact support.",
                "details": {},
                "request_id": request_id,
            }
        },
    )

