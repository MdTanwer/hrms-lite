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
    data: List[EmployeeResponse] = Field(..., description="List of employees")

    class Config:
        schema_extra = {
            "example": {
                "total": 50,
                "page": 1,
                "page_size": 10,
                "total_pages": 5,
                "data": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "employee_id": "EMP001",
                        "full_name": "John Doe",
                        "email": "john.doe@company.com",
                        "department": "Engineering",
                        "position": "Senior Developer",
                        "salary": 75000.0,
                        "start_date": "2022-01-15",
                        "status": "active",
                        "created_at": "2022-01-15T10:00:00Z",
                        "updated_at": "2022-01-15T10:00:00Z"
                    }
                ]
            }
        }


class EmployeeStatsResponse(BaseModel):
    """Schema for employee statistics response"""
    total_employees: int = Field(..., ge=0, description="Total number of employees")
    active_employees: int = Field(..., ge=0, description="Number of active employees")
    inactive_employees: int = Field(..., ge=0, description="Number of inactive employees")
    on_leave_employees: int = Field(..., ge=0, description="Number of employees on leave")
    department_breakdown: Dict[str, int] = Field(..., description="Employee count by department")
    average_salary: float = Field(..., ge=0, description="Average salary across all employees")
    recent_hires: List[EmployeeResponse] = Field(..., description="Last 5 employees hired")

    class Config:
        schema_extra = {
            "example": {
                "total_employees": 25,
                "active_employees": 22,
                "inactive_employees": 2,
                "on_leave_employees": 1,
                "department_breakdown": {
                    "Engineering": 10,
                    "HR": 5,
                    "Sales": 6,
                    "Marketing": 4
                },
                "average_salary": 65000.0,
                "recent_hires": [
                    {
                        "id": "507f1f77bcf86cd799439012",
                        "employee_id": "EMP025",
                        "full_name": "Jane Smith",
                        "email": "jane.smith@company.com",
                        "department": "Engineering",
                        "position": "Junior Developer",
                        "salary": 55000.0,
                        "start_date": "2024-01-10",
                        "status": "active",
                        "created_at": "2024-01-10T09:00:00Z",
                        "updated_at": "2024-01-10T09:00:00Z"
                    }
                ]
            }
        }
