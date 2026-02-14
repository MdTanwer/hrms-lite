"""API response schemas for attendance. Domain models live in app.models.attendance."""

from typing import List, Dict, Any
from pydantic import BaseModel

from app.models.attendance import AttendanceResponse


class AttendanceListResponse(BaseModel):
    """Paginated list of attendance records."""

    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[AttendanceResponse]


class AttendanceStatsResponse(BaseModel):
    """Attendance statistics over a date range."""

    total_records: int
    present_count: int
    absent_count: int
    half_day_count: int
    leave_count: int
    attendance_rate: float
    date_range: Dict[str, Any]


class EmployeeAttendanceReport(BaseModel):
    """Per-employee attendance summary for reports."""

    employee_id: str
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
