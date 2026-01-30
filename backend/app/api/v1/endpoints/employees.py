from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_database
from app.crud.employee import employee_crud
from app.crud.attendance import attendance_crud
from app.models.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB
from app.schemas.employee import EmployeeListResponse, EmployeeStatsResponse
from app.schemas.common import APIResponse, ErrorResponse, SuccessResponse
from bson import ObjectId, errors as bson_errors

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post(
    "",
    response_model=APIResponse[EmployeeInDB],
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee",
    description="Create a new employee record with validation for unique employee_id and email.",
    responses={
        201: {
            "description": "Employee created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Employee created successfully",
                        "data": {
                            "id": "507f1f77bcf86cd799439011",
                            "employee_id": "EMP001",
                            "full_name": "John Doe",
                            "email": "john.doe@company.com",
                            "department": "Engineering",
                            "position": "Software Engineer",
                            "salary": 75000.00,
                            "start_date": "2024-01-15",
                            "status": "active",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        },
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error - duplicate employee_id or email",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid data format",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse
        }
    }
)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new employee with validation.
    
    - **employee_id**: Must be unique and follow format EMPXXX
    - **email**: Must be unique and valid email format
    - **department**: Must be one of the predefined departments
    - **salary**: Must be within valid range (20000-200000)
    """
    try:
        logger.info(f"Creating new employee: {employee_data.employee_id}")
        
        # Create employee (validation handled in CRUD)
        employee = await employee_crud.create(db, employee_data)
        
        logger.info(f"Employee created successfully: {employee.employee_id}")
        return APIResponse(
            data=employee,
            message="Employee created successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee"
        )


@router.get(
    "",
    response_model=EmployeeListResponse,
    summary="Get all employees with pagination and filters",
    description="Retrieve a paginated list of employees with optional filtering by department, status, or search term.",
    responses={
        200: {
            "description": "Employees retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total": 50,
                        "page": 1,
                        "page_size": 10,
                        "total_pages": 5,
                        "data": [
                            {
                                "id": "507f1f77bcf86cd799439011",
                                "employee_id": "EMP001",
                                "full_name": "John Doe",
                                "email": "john.doe@company.com",
                                "department": "Engineering",
                                "position": "Software Engineer",
                                "salary": 75000.00,
                                "start_date": "2024-01-15",
                                "status": "active"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search across name, email, employee_id"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get employees with optional filtering and pagination.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (1-100)
    - **department**: Filter by specific department
    - **status**: Filter by employee status (active, inactive, on-leave)
    - **search**: Search term for name, email, or employee_id (case-insensitive)
    """
    try:
        logger.info(f"Getting employees: skip={skip}, limit={limit}, department={department}, status={status}, search={search}")
        
        # Build filter and query based on parameters
        if search:
            employees = await employee_crud.search_employees(db, search, skip, limit)
            total = await employee_crud.count(db, {
                "$or": [
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"employee_id": {"$regex": search, "$options": "i"}},
                    {"position": {"$regex": search, "$options": "i"}}
                ]
            })
        elif department:
            employees = await employee_crud.get_by_department(db, department, skip, limit)
            total = await employee_crud.count(db, {"department": department})
        elif status:
            employees = await employee_crud.get_by_status(db, status, skip, limit)
            total = await employee_crud.count(db, {"status": status})
        else:
            employees = await employee_crud.get_multi(db, skip, limit)
            total = await employee_crud.count(db)
        
        total_pages = (total + limit - 1) // limit
        
        logger.info(f"Retrieved {len(employees)} employees out of {total} total")
        
        return EmployeeListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=employees
        )
        
    except Exception as e:
        logger.error(f"Error getting employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employees"
        )


@router.get(
    "/{employee_id}",
    response_model=APIResponse[EmployeeInDB],
    summary="Get employee by employee_id",
    description="Retrieve a specific employee using their employee_id (e.g., EMP001).",
    responses={
        200: {
            "description": "Employee retrieved successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        }
    }
)
async def get_employee_by_id(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get employee by employee_id.
    
    - **employee_id**: The employee ID (e.g., EMP001)
    """
    try:
        logger.info(f"Getting employee by employee_id: {employee_id}")
        
        employee = await employee_crud.get_by_employee_id(db, employee_id)
        
        if not employee:
            logger.warning(f"Employee not found: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        logger.info(f"Employee retrieved: {employee_id}")
        return APIResponse(data=employee)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee"
        )


@router.get(
    "/id/{id}",
    response_model=APIResponse[EmployeeInDB],
    summary="Get employee by MongoDB ObjectId",
    description="Retrieve a specific employee using their MongoDB document ID.",
    responses={
        200: {
            "description": "Employee retrieved successfully"
        },
        400: {
            "description": "Invalid ObjectId format",
            "model": ErrorResponse
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        }
    }
)
async def get_employee_by_object_id(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get employee by MongoDB ObjectId.
    
    - **id**: The MongoDB document ID
    """
    try:
        logger.info(f"Getting employee by ObjectId: {id}")
        
        employee = await employee_crud.get(db, id)
        
        if not employee:
            logger.warning(f"Employee not found with ObjectId: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        logger.info(f"Employee retrieved by ObjectId: {id}")
        return APIResponse(data=employee)
        
    except ValueError as e:
        logger.warning(f"Invalid ObjectId format: {id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee by ObjectId {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee"
        )


@router.put(
    "/{employee_id}",
    response_model=APIResponse[EmployeeInDB],
    summary="Update employee (full update)",
    description="Update all fields of an employee record. All fields are required.",
    responses={
        200: {
            "description": "Employee updated successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        },
        400: {
            "description": "Duplicate email or employee_id",
            "model": ErrorResponse
        }
    }
)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update employee (full update).
    
    - **employee_id**: The employee ID to update
    - **employee_data**: Complete employee data (all fields)
    """
    try:
        logger.info(f"Updating employee: {employee_id}")
        
        # Get current employee to get MongoDB ID
        current_employee = await employee_crud.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        # Update employee
        updated_employee = await employee_crud.update(db, str(current_employee.id), employee_data)
        
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        logger.info(f"Employee updated successfully: {employee_id}")
        return APIResponse(
            data=updated_employee,
            message="Employee updated successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )


@router.patch(
    "/{employee_id}",
    response_model=APIResponse[EmployeeInDB],
    summary="Partial update employee",
    description="Update specific fields of an employee record. Only provided fields will be updated.",
    responses={
        200: {
            "description": "Employee updated successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        },
        400: {
            "description": "Duplicate email or employee_id",
            "model": ErrorResponse
        }
    }
)
async def partial_update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Partial update employee.
    
    - **employee_id**: The employee ID to update
    - **employee_data**: Partial employee data (only provided fields will be updated)
    """
    try:
        logger.info(f"Partially updating employee: {employee_id}")
        
        # Get current employee to get MongoDB ID
        current_employee = await employee_crud.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        # Update employee (partial update handled in CRUD)
        updated_employee = await employee_crud.update(db, str(current_employee.id), employee_data)
        
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        logger.info(f"Employee partially updated successfully: {employee_id}")
        return APIResponse(
            data=updated_employee,
            message="Employee updated successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error partially updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error partially updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )


@router.delete(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="Delete employee",
    description="Delete an employee record. Performs soft delete by setting status to 'inactive'.",
    responses={
        200: {
            "description": "Employee deleted successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        }
    }
)
async def delete_employee(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete employee (soft delete).
    
    - **employee_id**: The employee ID to delete
    
    Note: This performs a soft delete by setting status to 'inactive'.
    The employee record is preserved for historical data integrity.
    """
    try:
        logger.info(f"Deleting employee: {employee_id}")
        
        # Get current employee
        current_employee = await employee_crud.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        # Check if employee has attendance records
        attendance_count = await attendance_crud.count(db, {"employee_id": employee_id.upper()})
        if attendance_count > 0:
            logger.info(f"Employee {employee_id} has {attendance_count} attendance records, performing soft delete")
            # Soft delete by setting status to inactive
            update_data = EmployeeUpdate(status="inactive")
            await employee_crud.update(db, str(current_employee.id), update_data)
            message = f"Employee {employee_id} deactivated (soft delete due to attendance records)"
        else:
            # Hard delete if no attendance records
            await employee_crud.delete(db, str(current_employee.id))
            message = f"Employee {employee_id} deleted successfully"
        
        logger.info(f"Employee deletion completed: {employee_id}")
        return SuccessResponse(message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee"
        )


@router.get(
    "/department/{department}",
    response_model=EmployeeListResponse,
    summary="Get employees by department",
    description="Retrieve all employees belonging to a specific department.",
    responses={
        200: {
            "description": "Employees retrieved successfully"
        }
    }
)
async def get_employees_by_department(
    department: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get employees by department.
    
    - **department**: Department name to filter by
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (1-100)
    """
    try:
        logger.info(f"Getting employees by department: {department}")
        
        employees = await employee_crud.get_by_department(db, department, skip, limit)
        total = await employee_crud.count(db, {"department": department})
        total_pages = (total + limit - 1) // limit
        
        logger.info(f"Retrieved {len(employees)} employees from department {department}")
        
        return EmployeeListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=employees
        )
        
    except Exception as e:
        logger.error(f"Error getting employees by department {department}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employees by department"
        )


@router.get(
    "/stats",
    response_model=APIResponse[EmployeeStatsResponse],
    summary="Get employee statistics",
    description="Retrieve comprehensive employee statistics including counts by status, department breakdown, average salary, and recent hires.",
    responses={
        200: {
            "description": "Statistics retrieved successfully"
        }
    }
)
async def get_employee_stats(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get comprehensive employee statistics.
    
    Returns:
    - Total employee count by status
    - Department breakdown with counts
    - Average salary across all employees
    - Recent hires (last 30 days)
    """
    try:
        logger.info("Getting employee statistics")
        
        stats = await employee_crud.get_employee_stats(db)
        
        # Convert to response format
        stats_response = EmployeeStatsResponse(
            total_employees=stats["total_employees"],
            active_employees=stats["active_employees"],
            inactive_employees=stats["inactive_employees"],
            on_leave_employees=stats["on_leave_employees"],
            department_breakdown=stats["department_breakdown"],
            average_salary=stats["average_salary"],
            recent_hires=stats["recent_hires"]
        )
        
        logger.info("Employee statistics retrieved successfully")
        return APIResponse(
            data=stats_response,
            message="Employee statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting employee statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee statistics"
        )
