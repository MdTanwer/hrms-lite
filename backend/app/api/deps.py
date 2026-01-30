import logging
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Query, Depends, HTTPException, status
from app.config.database import get_database

logger = logging.getLogger(__name__)


async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency to get database instance.
    
    Usage:
        db: AsyncIOMotorDatabase = Depends(get_database)
    
    Yields:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Raises:
        HTTPException: If database connection fails
    """
    try:
        database = await get_database()
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
    """
    Pagination parameters for API endpoints.
    
    Provides consistent pagination across all endpoints with validation
    and sensible defaults.
    
    Usage:
        pagination: PaginationParams = Depends()
    """
    
    def __init__(
        self,
        skip: int = Query(
            0, 
            ge=0, 
            description="Number of records to skip for pagination"
        ),
        limit: int = Query(
            100, 
            ge=1, 
            le=100, 
            description="Maximum number of records to return (1-100)"
        )
    ):
        self.skip = skip
        self.limit = limit
    
    @property
    def page(self) -> int:
        """Calculate current page number (1-based)"""
        return (self.skip // self.limit) + 1
    
    @property
    def offset(self) -> int:
        """Get offset for database queries"""
        return self.skip
    
    def get_skip_for_page(self, page: int) -> int:
        """Calculate skip value for a specific page number"""
        return (page - 1) * self.limit


class SearchParams:
    """
    Search parameters for API endpoints.
    
    Provides consistent search functionality across endpoints.
    
    Usage:
        search: SearchParams = Depends()
    """
    
    def __init__(
        self,
        search: str = Query(
            None,
            min_length=1,
            max_length=100,
            description="Search term for filtering results"
        )
    ):
        self.search = search.strip() if search else None
    
    def is_valid(self) -> bool:
        """Check if search term is valid"""
        return self.search is not None and len(self.search) > 0


class DateRangeParams:
    """
    Date range parameters for API endpoints.
    
    Provides consistent date filtering across endpoints.
    
    Usage:
        date_range: DateRangeParams = Depends()
    """
    
    def __init__(
        self,
        start_date: str = Query(
            None,
            description="Start date in YYYY-MM-DD format"
        ),
        end_date: str = Query(
            None,
            description="End date in YYYY-MM-DD format"
        )
    ):
        self.start_date = start_date
        self.end_date = end_date


class SortParams:
    """
    Sorting parameters for API endpoints.
    
    Provides consistent sorting functionality across endpoints.
    
    Usage:
        sort: SortParams = Depends()
    """
    
    def __init__(
        self,
        sort_by: str = Query(
            "created_at",
            description="Field to sort by"
        ),
        sort_order: str = Query(
            "desc",
            regex="^(asc|desc)$",
            description="Sort order: asc or desc"
        )
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order
    
    @property
    def sort_direction(self) -> int:
        """Get MongoDB sort direction (1 for asc, -1 for desc)"""
        return 1 if self.sort_order == "asc" else -1


# Future dependencies (placeholders for future implementation)

async def get_current_user():
    """
    Dependency to get current authenticated user.
    
    Placeholder for future authentication implementation.
    
    Usage:
        current_user = Depends(get_current_user)
    """
    # TODO: Implement JWT authentication
    pass


def rate_limiter(limit: int = 100, window: int = 60):
    """
    Rate limiting dependency.
    
    Placeholder for future rate limiting implementation.
    
    Args:
        limit: Number of requests allowed
        window: Time window in seconds
        
    Usage:
        @router.get("/", dependencies=[Depends(rate_limiter(10, 60))])
    """
    # TODO: Implement rate limiting using Redis or in-memory store
    pass


def require_permissions(permission: str):
    """
    Permission-based access control dependency.
    
    Placeholder for future RBAC implementation.
    
    Args:
        permission: Required permission
        
    Usage:
        @router.get("/", dependencies=[Depends(require_permissions("admin"))])
    """
    # TODO: Implement role-based access control
    pass


# Utility functions for dependency injection

def validate_employee_id(employee_id: str) -> str:
    """
    Validate employee ID format.
    
    Args:
        employee_id: Employee ID to validate
        
    Returns:
        str: Validated employee ID (uppercase)
        
    Raises:
        HTTPException: If employee ID format is invalid
    """
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID is required"
        )
    
    # Basic validation - can be enhanced
    if len(employee_id) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID must be at least 3 characters long"
        )
    
    return employee_id.upper()


def validate_date_format(date_string: str) -> str:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_string: Date string to validate
        
    Returns:
        str: Validated date string
        
    Raises:
        HTTPException: If date format is invalid
    """
    from datetime import datetime
    
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )


# Combined dependencies for common use cases

class CommonQueryParams:
    """
    Combined common query parameters.
    
    Includes pagination, search, and sorting for convenience.
    
    Usage:
        params: CommonQueryParams = Depends()
    """
    
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
    """
    Employee-specific query parameters.
    
    Includes common parameters plus employee-specific filters.
    
    Usage:
        params: EmployeeQueryParams = Depends()
    """
    
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
    """
    Attendance-specific query parameters.
    
    Includes common parameters plus attendance-specific filters.
    
    Usage:
        params: AttendanceQueryParams = Depends()
    """
    
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
