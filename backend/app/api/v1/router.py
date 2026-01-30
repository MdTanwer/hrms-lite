from fastapi import APIRouter
from app.api.v1.endpoints import employees
# from app.api.v1.endpoints import attendance, dashboard

api_router = APIRouter()

# Include all routers
api_router.include_router(employees.router)
# api_router.include_router(attendance.router)
# api_router.include_router(dashboard.router)
