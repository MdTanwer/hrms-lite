import logging
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Query, Depends, HTTPException, status
from app.config.database import get_database as get_db_connection

logger = logging.getLogger(__name__)


async def get_database_dependency() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    try:
        database = await get_db_connection()
        if not database:
            logger.error("Database connection failed - database is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        logger.debug("Database dependency injected successfully")
        yield database
        
    except Exception as e:
        logger.error(f"Database dependency error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return (1-100)")
    ):
        self.skip = skip
        self.limit = limit
    
    @property
    def page(self) -> int:
        return (self.skip // self.limit) + 1
    
    @property
    def offset(self) -> int:
        return self.skip
    
    def get_skip_for_page(self, page: int) -> int:
        return (page - 1) * self.limit


class SearchParams:
    def __init__(
        self,
        search: str = Query(None, min_length=1, max_length=100, description="Search term for filtering results")
    ):
        self.search = search.strip() if search else None
    
    def is_valid(self) -> bool:
        return self.search is not None and len(self.search) > 0


class DateRangeParams:
    def __init__(
        self,
        start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(None, description="End date in YYYY-MM-DD format")
    ):
        self.start_date = start_date
        self.end_date = end_date


class SortParams:
    def __init__(
        self,
        sort_by: str = Query("created_at", description="Field to sort by"),
        sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc")
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order
    
    @property
    def sort_direction(self) -> int:
        return 1 if self.sort_order == "asc" else -1


async def get_current_user():
    pass


def rate_limiter(limit: int = 100, window: int = 60):
    pass


def require_permissions(permission: str):
    pass


def validate_employee_id(employee_id: str) -> str:
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID is required"
        )
    
    if len(employee_id) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID must be at least 3 characters long"
        )
    
    return employee_id.upper()


def validate_date_format(date_string: str) -> str:
    from datetime import datetime
    
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )


class CommonQueryParams:
    def __init__(
        self,
        pagination: PaginationParams = Depends(),
        search: SearchParams = Depends(),
        sort: SortParams = Depends()
    ):
        self.pagination = pagination
        self.search = search
        self.sort = sort


class EmployeeQueryParams:
    def __init__(
        self,
        pagination: PaginationParams = Depends(),
        search: SearchParams = Depends(),
        sort: SortParams = Depends(),
        department: str = Query(None, description="Filter by department"),
        status: str = Query(None, description="Filter by employee status")
    ):
        self.pagination = pagination
        self.search = search
        self.sort = sort
        self.department = department
        self.status = status


class AttendanceQueryParams:
    def __init__(
        self,
        pagination: PaginationParams = Depends(),
        search: SearchParams = Depends(),
        sort: SortParams = Depends(),
        employee_id: str = Query(None, description="Filter by employee ID"),
        status: str = Query(None, description="Filter by attendance status"),
        date_range: DateRangeParams = Depends()
    ):
        self.pagination = pagination
        self.search = search
        self.sort = sort
        self.employee_id = employee_id
        self.status = status
        self.date_range = date_range
