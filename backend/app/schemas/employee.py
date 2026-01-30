from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    """Base employee schema"""
    employee_id: str = Field(..., description="Unique employee identifier")
    full_name: str = Field(..., min_length=1, max_length=100, description="Employee full name")
    email: str = Field(..., description="Employee email address")
    department: str = Field(..., description="Department name")
    position: str = Field(..., description="Job position")
    salary: float = Field(..., gt=0, description="Annual salary")
    start_date: date = Field(..., description="Employment start date")
    status: str = Field(..., description="Employee status")


class EmployeeCreate(EmployeeBase):
    """Schema for creating new employees"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating employee records"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee responses"""
    id: str = Field(..., description="MongoDB document ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for paginated employee list responses"""
    total: int = Field(..., ge=0, description="Total count of employees")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    data: List[Dict] = Field(..., description="List of employees")


class EmployeeStatsResponse(BaseModel):
    """Schema for employee statistics response"""
    total_employees: int = Field(..., ge=0, description="Total number of employees")
    active_employees: int = Field(..., ge=0, description="Number of active employees")
    inactive_employees: int = Field(..., ge=0, description="Number of inactive employees")
    on_leave_employees: int = Field(..., ge=0, description="Number of employees on leave")
    department_breakdown: Dict[str, int] = Field(..., description="Employee count by department")
    average_salary: float = Field(..., ge=0, description="Average salary across all employees")
    recent_hires: List[Dict] = Field(..., description="Last 5 employees hired")
