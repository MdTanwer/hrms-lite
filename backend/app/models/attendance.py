"""Attendance domain models. Server-set: marked_at."""

from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from bson import ObjectId


class AttendanceBase(BaseModel):
    """Fields shared by create and DB document. employee_id stored as ObjectId in DB, serialized as str in API."""

    employee_id: str

    @field_validator("employee_id", mode="before")
    @classmethod
    def employee_id_objectid_to_str(cls, v):
        """Accept ObjectId from DB and serialize to str for API."""
        if isinstance(v, ObjectId):
            return str(v)
        return v
    date: date
    status: Literal["present", "absent", "half-day", "leave"] = "present"
    notes: Optional[str] = None
    marked_by: str = "Admin"
    marked_at: Optional[datetime] = None  # Set by server on create; optional on input


class AttendanceCreate(AttendanceBase):
    """Request body for marking attendance. marked_at is server-set."""

    pass


class AttendanceInDB(AttendanceBase):
    """Document shape as stored and returned. id maps from MongoDB _id."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    marked_at: datetime = Field(..., description="Server-set when attendance is marked")

    @field_validator("id", mode="before")
    @classmethod
    def objectid_to_str(cls, v):  # noqa: N805
        if isinstance(v, ObjectId):
            return str(v)
        return v


class AttendanceResponse(AttendanceInDB):
    """Attendance with optional join fields (e.g. from aggregation)."""

    employee_name: Optional[str] = None
    employee_department: Optional[str] = None
    employee_position: Optional[str] = None
