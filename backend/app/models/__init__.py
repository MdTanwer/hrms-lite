"""Domain models for the HRMS application."""

from app.models.employee import EmployeeCreate, EmployeeInDB
from app.models.attendance import (
    AttendanceCreate,
    AttendanceInDB,
    AttendanceResponse,
)

__all__ = [
    "EmployeeCreate",
    "EmployeeInDB",
    "AttendanceCreate",
    "AttendanceInDB",
    "AttendanceResponse",
]
