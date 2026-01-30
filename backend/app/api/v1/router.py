from fastapi import APIRouter
from app.api.v1.endpoints import employees, attendance, dashboard

api_router = APIRouter()

# Include all routers
api_router.include_router(employees.router)
api_router.include_router(attendance.router)
api_router.include_router(dashboard.router)

# API version info endpoint
@api_router.get("/info", summary="API version information", description="Get API version and available endpoints.")
async def api_info():
    """
    Get API version information and available endpoints.
    
    Returns:
        API version information and list of available endpoint groups.
    """
    return {
        "version": "1.0.0",
        "title": "HRMS Lite API",
        "description": "Human Resource Management System API v1",
        "endpoints": [
            "/employees",
            "/attendance", 
            "/dashboard"
        ],
        "features": [
            "Employee Management",
            "Attendance Tracking",
            "Statistics & Reporting"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }
