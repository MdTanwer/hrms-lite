import re
from typing import Any
from pydantic import validator


def validate_employee_id(employee_id: str) -> str:
    """Validate employee ID format"""
    if not re.match(r'^EMP\d{3,}$', employee_id):
        raise ValueError("Employee ID must start with 'EMP' followed by numbers (e.g., EMP001)")
    return employee_id


def validate_email_format(email: str) -> str:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email


def validate_salary(salary: float) -> float:
    """Validate salary is positive and reasonable"""
    if salary <= 0:
        raise ValueError("Salary must be greater than 0")
    if salary > 10000000:  # 10 million as upper limit
        raise ValueError("Salary seems unreasonably high")
    return salary


def validate_department(department: str) -> str:
    """Validate department name"""
    if not department or len(department.strip()) < 2:
        raise ValueError("Department name must be at least 2 characters")
    if len(department) > 50:
        raise ValueError("Department name cannot exceed 50 characters")
    return department.strip().title()


def validate_position(position: str) -> str:
    """Validate position name"""
    if not position or len(position.strip()) < 2:
        raise ValueError("Position name must be at least 2 characters")
    if len(position) > 100:
        raise ValueError("Position name cannot exceed 100 characters")
    return position.strip().title()


def validate_full_name(name: str) -> str:
    """Validate full name"""
    if not name or len(name.strip()) < 2:
        raise ValueError("Full name must be at least 2 characters")
    if len(name) > 100:
        raise ValueError("Full name cannot exceed 100 characters")
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name.strip()):
        raise ValueError("Full name can only contain letters, spaces, hyphens, and apostrophes")
    
    return name.strip().title()


def validate_status(status: str) -> str:
    """Validate employee status"""
    valid_statuses = ['active', 'inactive', 'on-leave']
    if status.lower() not in valid_statuses:
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
    return status.lower()


def validate_attendance_status(status: str) -> str:
    """Validate attendance status"""
    valid_statuses = ['present', 'absent']
    if status.lower() not in valid_statuses:
        raise ValueError(f"Attendance status must be one of: {', '.join(valid_statuses)}")
    return status.lower()


class EmployeeValidators:
    """Collection of employee validators for Pydantic models"""
    
    @validator('employee_id')
    def employee_id_validator(cls, v):
        return validate_employee_id(v)
    
    @validator('email')
    def email_validator(cls, v):
        return validate_email_format(v)
    
    @validator('salary')
    def salary_validator(cls, v):
        return validate_salary(v)
    
    @validator('department')
    def department_validator(cls, v):
        return validate_department(v)
    
    @validator('position')
    def position_validator(cls, v):
        return validate_position(v)
    
    @validator('full_name')
    def full_name_validator(cls, v):
        return validate_full_name(v)
    
    @validator('status')
    def status_validator(cls, v):
        return validate_status(v)


class AttendanceValidators:
    """Collection of attendance validators for Pydantic models"""
    
    @validator('status')
    def status_validator(cls, v):
        return validate_attendance_status(v)
