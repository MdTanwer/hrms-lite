"""API response schemas for attendance. Domain models live in app.models.attendance."""

from typing import List
from pydantic import BaseModel


class AttendanceListItem(BaseModel):
    """Single attendance row for list API; frontend displays as-is (id, date, status)."""

    id: str
    date: str  # ISO date string for display
    status: str

    @classmethod
    def from_attendance(cls, att: object) -> "AttendanceListItem":
        """Build display-ready item from attendance model (id, date as ISO string, status)."""
        d = getattr(att, "date", None)
        date_str = d.isoformat() if hasattr(d, "isoformat") else str(d) if d else ""
        return cls(
            id=getattr(att, "id", ""),
            date=date_str,
            status=getattr(att, "status", "present") or "present",
        )


class AttendanceListResponse(BaseModel):
    """Paginated list of attendance records. data is display-ready for the table."""

    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[AttendanceListItem]


class EmployeeAttendanceStatsResponse(BaseModel):
    """Aggregated attendance stats for one employee over a date range."""

    total_days: int
    present_days: int
    absent_days: int
    half_days: int
    leave_days: int
    attendance_rate: float


