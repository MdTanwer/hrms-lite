"""Shared request/response schemas used across API endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper with optional data payload."""

    success: bool = Field(default=True, description="Whether the operation succeeded")
    message: str = Field(default="Success", description="Response message")
    data: Optional[T] = Field(None, description="Response data payload")
    errors: Optional[List[str]] = Field(None, description="Error details if any")
    timestamp: datetime = Field(default_factory=_utc_now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "507f1f77bcf86cd799439011", "name": "Sample Data"},
                "errors": None,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    success: bool = Field(default=False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    errors: Optional[List[str]] = Field(None, description="Detailed error messages")
    timestamp: datetime = Field(default_factory=_utc_now, description="Error timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Validation failed",
                "errors": ["Employee ID is required", "Email format is invalid"],
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    success: bool = Field(default=True, description="Whether the operation succeeded")
    message: str = Field(default="Data retrieved successfully", description="Response message")
    data: Optional[T] = Field(None, description="Paginated data payload")
    pagination: Dict[str, Any] = Field(..., description="Pagination metadata")
    timestamp: datetime = Field(default_factory=_utc_now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
                "pagination": {"total": 100, "page": 1, "page_size": 10, "total_pages": 10},
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
    )


class SuccessResponse(BaseModel):
    """Success response for operations that do not return a data payload."""

    success: bool = Field(default=True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=_utc_now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Employee deleted successfully",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
    )


__all__ = [
    "APIResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
]
