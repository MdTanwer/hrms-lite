from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AttendanceBase(BaseModel):
    """Base attendance model with common fields"""
    employee_id: str = Field(..., description="Employee ID (must match existing employee)")
    date: date = Field(..., description="Attendance date")
    status: Literal["present", "absent", "half-day", "leave"] = Field(default="present", description="Attendance status")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes (max 500 characters)")
    marked_by: str = Field(default="Admin", description="Who marked the attendance (for future auth system)")

    @validator('status')
    def validate_status(cls, v):
        """Validate attendance status"""
        valid_statuses = ["present", "absent", "half-day", "leave"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @validator('notes')
    def validate_notes_length(cls, v):
        """Validate notes length"""
        if v is not None and len(v.strip()) == 0:
            return None
        if v is not None and len(v) > 500:
            raise ValueError("Notes cannot exceed 500 characters")
        return v.strip() if v else None


class AttendanceCreate(AttendanceBase):
    """Model for creating new attendance records"""
    
    @validator('date')
    def validate_date_not_future(cls, v):
        """Ensure attendance date is not in the future"""
        if v > date.today():
            raise ValueError('Attendance date cannot be in the future')
        return v

    @validator('date')
    def validate_date_format(cls, v):
        """Validate date format and ensure it's a valid date"""
        if isinstance(v, str):
            try:
                # Try to parse string date
                parsed_date = datetime.strptime(v, '%Y-%m-%d').date()
                return parsed_date
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @validator('employee_id')
    def validate_employee_id_format(cls, v):
        """Validate employee ID format"""
        import re
        if not re.match(r'^EMP\d{3,}$', v):
            raise ValueError('Employee ID must be in format EMP001, EMP002, etc.')
        return v.upper()


class AttendanceUpdate(BaseModel):
    """Model for updating attendance records"""
    status: Optional[Literal["present", "absent", "half-day", "leave"]] = Field(None, description="Attendance status")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes (max 500 characters)")

    @validator('status')
    def validate_status(cls, v):
        """Validate attendance status"""
        if v is None:
            return v
        valid_statuses = ["present", "absent", "half-day", "leave"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @validator('notes')
    def validate_notes_length(cls, v):
        """Validate notes length"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v) > 500:
            raise ValueError("Notes cannot exceed 500 characters")
        return v.strip()


class AttendanceInDB(AttendanceBase):
    """Database model for attendance records"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    marked_at: datetime = Field(default_factory=datetime.utcnow, description="When attendance was marked")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "employee_id": "EMP001",
                "date": "2024-01-15",
                "status": "present",
                "notes": "On time",
                "marked_by": "Admin",
                "created_at": "2024-01-15T09:00:00Z",
                "updated_at": "2024-01-15T09:00:00Z",
                "marked_at": "2024-01-15T09:00:00Z"
            }
        }


class AttendanceResponse(AttendanceInDB):
    """API response model for attendance records"""
    employee_name: Optional[str] = Field(None, description="Employee full name (populated via join)")
    employee_department: Optional[str] = Field(None, description="Employee department (populated via join)")
    employee_position: Optional[str] = Field(None, description="Employee position (populated via join)")

    @validator('date')
    def format_date(cls, v):
        """Format date for API response"""
        return v.isoformat() if isinstance(v, date) else v

    @validator('created_at', 'updated_at', 'marked_at')
    def format_datetime(cls, v):
        """Format datetime for API response"""
        return v.isoformat() if isinstance(v, datetime) else v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AttendanceFilter(BaseModel):
    """Model for attendance query parameters and filtering"""
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    start_date: Optional[date] = Field(None, description="Filter attendance from this date (inclusive)")
    end_date: Optional[date] = Field(None, description="Filter attendance to this date (inclusive)")
    status: Optional[Literal["present", "absent", "half-day", "leave"]] = Field(None, description="Filter by attendance status")
    department: Optional[str] = Field(None, description="Filter by employee department")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end_date is not before start_date"""
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v

    @validator('employee_id')
    def validate_employee_id_format(cls, v):
        """Validate employee ID format"""
        if v is None:
            return v
        import re
        if not re.match(r'^EMP\d{3,}$', v):
            raise ValueError('Employee ID must be in format EMP001, EMP002, etc.')
        return v.upper()


class AttendanceListResponse(BaseModel):
    """Model for paginated attendance list response"""
    attendances: list[AttendanceResponse] = Field(..., description="List of attendance records")
    total: int = Field(..., ge=0, description="Total number of attendance records")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Number of records per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class AttendanceStats(BaseModel):
    """Model for attendance statistics"""
    total_days: int = Field(..., ge=0, description="Total number of days")
    present_days: int = Field(..., ge=0, description="Number of present days")
    absent_days: int = Field(..., ge=0, description="Number of absent days")
    half_days: int = Field(..., ge=0, description="Number of half days")
    leave_days: int = Field(..., ge=0, description="Number of leave days")
    attendance_rate: float = Field(..., ge=0, le=100, description="Attendance rate percentage")


class DailyAttendanceStats(BaseModel):
    """Model for daily attendance statistics"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_employees: int = Field(..., ge=0, description="Total employees expected")
    present_count: int = Field(..., ge=0, description="Number of employees present")
    absent_count: int = Field(..., ge=0, description="Number of employees absent")
    half_day_count: int = Field(..., ge=0, description="Number of employees with half day")
    leave_count: int = Field(..., ge=0, description="Number of employees on leave")
    attendance_rate: float = Field(..., ge=0, le=100, description="Daily attendance rate percentage")


class EmployeeAttendanceSummary(BaseModel):
    """Model for individual employee attendance summary"""
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee full name")
    employee_department: str = Field(..., description="Employee department")
    total_days: int = Field(..., ge=0, description="Total days in period")
    present_days: int = Field(..., ge=0, description="Number of present days")
    absent_days: int = Field(..., ge=0, description="Number of absent days")
    half_days: int = Field(..., ge=0, description="Number of half days")
    leave_days: int = Field(..., ge=0, description="Number of leave days")
    attendance_rate: float = Field(..., ge=0, le=100, description="Attendance rate percentage")
