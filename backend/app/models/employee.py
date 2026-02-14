import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from bson import ObjectId


class EmployeeBase(BaseModel):
    """Base employee fields; accepts camelCase (employeeId, fullName) or snake_case from API."""

    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(..., alias="employeeId", description="Unique employee ID (e.g., EMP001)")
    full_name: str = Field(
        ..., alias="fullName", min_length=2, max_length=100, description="Employee full name"
    )
    email: EmailStr = Field(..., description="Employee email address")
    department: str = Field(..., description="Employee department")
    position: Optional[str] = Field(None, description="Job position")
    status: str = Field("active", description="Employee status")

    @field_validator('employee_id')
    def validate_employee_id(cls, v):
        if not v:
            raise ValueError('Employee ID is required')
        v = v.upper()
        employee_id_pattern = r'^EMP\d{1,6}$'
        if not re.match(employee_id_pattern, v):
            raise ValueError('Invalid employee ID format. Must be EMP followed by 1-6 digits (e.g., EMP1, EMP001, EMP1234)')
        return v

    @field_validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        v = v.lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|company\.com|org\.com|net\.com)$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeInDB(EmployeeBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    deleted_at: Optional[datetime] = Field(None, description="Set when employee is soft-deleted")

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
