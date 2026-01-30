from typing import Generic, TypeVar, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Generic type variable for API responses
T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper for consistent API responses"""
    success: bool = Field(default=True, description="Indicates if the operation was successful")
    message: str = Field(default="Success", description="Response message")
    data: Optional[T] = Field(None, description="Response data payload")
    errors: Optional[List[str]] = Field(None, description="List of error messages if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {
                    "id": "507f1f77bcf86cd799439011",
                    "name": "Sample Data"
                },
                "errors": None,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = Field(default=False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    errors: Optional[List[str]] = Field(None, description="Detailed error messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Validation failed",
                "errors": [
                    "Employee ID is required",
                    "Email format is invalid"
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    success: bool = Field(default=True, description="Indicates if the operation was successful")
    message: str = Field(default="Data retrieved successfully", description="Response message")
    data: Optional[T] = Field(None, description="Paginated data payload")
    pagination: dict = Field(..., description="Pagination information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 10
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Simple success response for operations that don't return data"""
    success: bool = Field(default=True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Employee deleted successfully",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
