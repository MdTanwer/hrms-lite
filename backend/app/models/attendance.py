from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel


class AttendanceBase(BaseModel):
    employee_id: str
    date: date
    status: Literal["present", "absent", "half-day", "leave"] = "present"
    notes: Optional[str] = None
    marked_by: str = "Admin"


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[Literal["present", "absent", "half-day", "leave"]] = None
    notes: Optional[str] = None


class AttendanceInDB(AttendanceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    marked_at: datetime


class AttendanceResponse(AttendanceInDB):
    employee_name: Optional[str] = None
    employee_department: Optional[str] = None
    employee_position: Optional[str] = None


class AttendanceStats(BaseModel):
    total_days: int
    present_days: int
    absent_days: int
    half_days: int
    leave_days: int
    attendance_rate: float


class EmployeeAttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    employee_department: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
