import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from bson import ObjectId


class EmployeeBase(BaseModel):
    employee_id: str = Field(..., description="Unique employee ID (e.g., EMP001)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Employee full name")
    email: EmailStr = Field(..., description="Employee email address")
    department: str = Field(..., description="Employee department")
    position: str = Field(..., description="Job position")
    status: str = Field(..., description="Employee status")

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
    id: str = Field(..., alias="_id")
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
