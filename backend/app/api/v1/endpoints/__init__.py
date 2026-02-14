"""
API v1 endpoints package.

This package contains all API v1 endpoint modules:
- employees: Employee management endpoints
- attendance: Attendance management endpoints

Each module exports a FastAPI APIRouter instance that can be included
in the main API router.
"""

from . import employees, attendance

# Export routers for convenient access
__all__ = [
    "employees",
    "attendance",
]
