"""Response schemas for employee API endpoints."""

from typing import List
from pydantic import BaseModel, Field
from app.models.employee import EmployeeInDB


class EmployeeListResponse(BaseModel):
    """Paginated list of employees."""

    total: int = Field(..., ge=0, description="Total count of employees")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    data: List[EmployeeInDB] = Field(..., description="List of employees")


__all__ = [
    "EmployeeListResponse",
]
