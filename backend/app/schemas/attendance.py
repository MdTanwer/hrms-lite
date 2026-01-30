from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field


class AttendanceBase(BaseModel):
    """Base attendance schema"""
    employee_id: str = Field(..., description="Employee ID")
    date: date = Field(..., description="Attendance date")
    status: str = Field(..., description="Attendance status")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    marked_by: str = Field(..., description="Who marked the attendance")


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance records"""
    pass


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance records"""
    status: Optional[str] = Field(None, description="Attendance status")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class AttendanceResponse(AttendanceBase):
    """Schema for attendance responses"""
    id: str = Field(..., description="MongoDB document ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    marked_at: datetime = Field(..., description="When attendance was marked")
    employee_name: Optional[str] = Field(None, description="Employee full name (populated via join)")
    employee_department: Optional[str] = Field(None, description="Employee department (populated via join)")

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    """Schema for paginated attendance list responses"""
    total: int = Field(..., ge=0, description="Total count of attendance records")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    data: List[AttendanceResponse] = Field(..., description="List of attendance records")

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
                "data": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "employee_id": "EMP001",
                        "date": "2024-01-15",
                        "status": "present",
                        "notes": "On time",
                        "marked_by": "Admin",
                        "created_at": "2024-01-15T09:00:00Z",
                        "updated_at": "2024-01-15T09:00:00Z",
                        "marked_at": "2024-01-15T09:00:00Z",
                        "employee_name": "John Doe",
                        "employee_department": "Engineering"
                    }
                ]
            }
        }


class AttendanceStatsResponse(BaseModel):
    """Schema for attendance statistics response"""
    total_records: int = Field(..., ge=0, description="Total number of attendance records")
    present_count: int = Field(..., ge=0, description="Number of present records")
    absent_count: int = Field(..., ge=0, description="Number of absent records")
    half_day_count: int = Field(..., ge=0, description="Number of half-day records")
    leave_count: int = Field(..., ge=0, description="Number of leave records")
    attendance_rate: float = Field(..., ge=0, le=100, description="Attendance rate percentage")
    date_range: Dict[str, date] = Field(..., description="Start and end dates for the statistics")

    class Config:
        schema_extra = {
            "example": {
                "total_records": 200,
                "present_count": 160,
                "absent_count": 25,
                "half_day_count": 10,
                "leave_count": 5,
                "attendance_rate": 80.0,
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            }
        }


class EmployeeAttendanceReport(BaseModel):
    """Schema for individual employee attendance report"""
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee full name")
    total_days: int = Field(..., ge=0, description="Total days in the period")
    present_days: int = Field(..., ge=0, description="Number of present days")
    absent_days: int = Field(..., ge=0, description="Number of absent days")
    attendance_percentage: float = Field(..., ge=0, le=100, description="Attendance percentage")

    class Config:
        schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "employee_name": "John Doe",
                "total_days": 22,
                "present_days": 20,
                "absent_days": 2,
                "attendance_percentage": 90.91
            }
        }
