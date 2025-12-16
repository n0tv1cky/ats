"""Common schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class PaginationResponse(BaseModel, Generic[T]):
    """Pagination response wrapper."""
    data: List[T]
    pagination: dict
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": {}
                }
            }
        }

