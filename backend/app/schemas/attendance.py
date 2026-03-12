from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel


class AttendanceBase(BaseModel):
    """Base attendance schema"""
    employee_id: str
    date: date
    status: str
    notes: Optional[str] = None
    marked_by: str


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance records"""
    pass


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance records"""
    status: Optional[str] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    marked_at: datetime
    employee_name: Optional[str] = None
    employee_department: Optional[str] = None


class AttendanceListResponse(BaseModel):
    """Schema for paginated attendance list responses"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[AttendanceResponse]


class AttendanceStatsResponse(BaseModel):
    """Schema for attendance statistics response"""
    total_records: int
    present_count: int
    absent_count: int
    half_day_count: int
    leave_count: int
    attendance_rate: float
    date_range: Dict[str, Any]


class DailyAttendanceStats(BaseModel):
    """Schema for daily attendance statistics"""
    total_employees: int
    present: int
    absent: int
    half_day: int
    leave: int
    attendance_rate: float


class EmployeeAttendanceReport(BaseModel):
    """Schema for individual employee attendance report"""
    employee_id: str
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
