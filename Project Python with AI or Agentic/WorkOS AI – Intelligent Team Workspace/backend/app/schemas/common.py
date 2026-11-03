from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standard success wrapper response."""
    success: bool = True
    data: DataT
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard pagination wrapper."""
    items: List[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail

