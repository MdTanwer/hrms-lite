from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, validator
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


class EmployeeBase(BaseModel):
    """Base employee model with common fields"""
    full_name: str = Field(..., min_length=2, max_length=100, description="Employee full name")
    email: EmailStr = Field(..., description="Employee email address")
    department: Literal["Engineering", "HR", "Sales", "Marketing", "Finance"] = Field(..., description="Employee department")
    position: str = Field(..., min_length=1, max_length=100, description="Job position")
    salary: float = Field(..., ge=15000, le=1000000, description="Annual salary (15,000 - 1,000,000)")
    start_date: date = Field(..., description="Employment start date")
    status: Literal["active", "inactive", "on-leave"] = Field(default="active", description="Employee status")

    @validator('email')
    def validate_email_domain(cls, v):
        """Validate email domain is professional"""
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com']
        domain = v.split('@')[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} is not allowed')
        return v.lower()

    @validator('salary')
    def validate_salary_range(cls, v):
        """Additional salary validation"""
        if v < 15000:
            raise ValueError('Salary must be at least 15,000')
        if v > 1000000:
            raise ValueError('Salary cannot exceed 1,000,000')
        return round(v, 2)


class EmployeeCreate(EmployeeBase):
    """Model for creating new employees"""
    employee_id: str = Field(..., description="Unique employee ID (e.g., EMP001)")

    @validator('employee_id')
    def validate_employee_id_format(cls, v):
        """Validate employee ID format: EMP followed by numbers"""
        import re
        if not re.match(r'^EMP\d{3,}$', v):
            raise ValueError('Employee ID must start with EMP followed by at least 3 digits (e.g., EMP001)')
        return v.upper()

    @validator('start_date')
    def validate_start_date_not_future(cls, v):
        """Ensure start date is not in the future"""
        if v > date.today():
            raise ValueError('Start date cannot be in the future')
        return v


class EmployeeUpdate(BaseModel):
    """Model for updating employee records"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Employee full name")
    email: Optional[EmailStr] = Field(None, description="Employee email address")
    department: Optional[Literal["Engineering", "HR", "Sales", "Marketing", "Finance"]] = Field(None, description="Employee department")
    position: Optional[str] = Field(None, min_length=1, max_length=100, description="Job position")
    salary: Optional[float] = Field(None, ge=15000, le=1000000, description="Annual salary (15,000 - 1,000,000)")
    status: Optional[Literal["active", "inactive", "on-leave"]] = Field(None, description="Employee status")

    @validator('email')
    def validate_email_domain(cls, v):
        """Validate email domain is professional"""
        if v is None:
            return v
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com']
        domain = v.split('@')[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} is not allowed')
        return v.lower()

    @validator('salary')
    def validate_salary_range(cls, v):
        """Additional salary validation"""
        if v is None:
            return v
        if v < 15000:
            raise ValueError('Salary must be at least 15,000')
        if v > 1000000:
            raise ValueError('Salary cannot exceed 1,000,000')
        return round(v, 2)

    @validator('*')
    def validate_at_least_one_field(cls, v, values):
        """Ensure at least one field is provided for update"""
        # This validator will be called for each field
        # We'll check if any field has a non-None value in the root validator
        return v

    @validator('*', pre=True, always=True)
    def root_validator(cls, values):
        """Root validator to ensure at least one field is provided"""
        if not any(v is not None for v in values.values()):
            raise ValueError('At least one field must be provided for update')
        return values


class EmployeeInDB(EmployeeBase):
    """Database model for employees"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id", description="MongoDB document ID")
    employee_id: str = Field(..., description="Unique employee ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
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
        }


class EmployeeResponse(EmployeeInDB):
    """API response model for employees"""
    
    @validator('start_date')
    def format_start_date(cls, v):
        """Format date for API response"""
        return v.isoformat() if isinstance(v, date) else v

    @validator('created_at', 'updated_at')
    def format_datetime(cls, v):
        """Format datetime for API response"""
        return v.isoformat() if isinstance(v, datetime) else v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EmployeeListResponse(BaseModel):
    """Model for paginated employee list response"""
    employees: list[EmployeeResponse] = Field(..., description="List of employees")
    total: int = Field(..., description="Total number of employees")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Number of employees per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class EmployeeStats(BaseModel):
    """Model for employee statistics"""
    total_employees: int = Field(..., ge=0, description="Total number of employees")
    active_employees: int = Field(..., ge=0, description="Number of active employees")
    inactive_employees: int = Field(..., ge=0, description="Number of inactive employees")
    on_leave_employees: int = Field(..., ge=0, description="Number of employees on leave")
    total_departments: int = Field(..., ge=0, description="Total number of departments")
    department_breakdown: dict[str, int] = Field(..., description="Employee count by department")
    average_salary: float = Field(..., ge=0, description="Average salary across all employees")
