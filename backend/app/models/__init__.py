"""Domain models for the HRMS application."""

from app.models.employee import EmployeeCreate, EmployeeInDB
from app.models.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceInDB,
    AttendanceResponse,
    AttendanceStats,
)

__all__ = [
    "EmployeeCreate",
    "EmployeeInDB",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceInDB",
    "AttendanceResponse",
    "AttendanceStats",
]
