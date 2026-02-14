"""Shared request/response schemas used across API endpoints."""

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar

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
    "SuccessResponse",
]
