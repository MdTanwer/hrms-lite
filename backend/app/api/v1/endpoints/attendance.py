from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_database
from app.crud.attendance import attendance_crud
from app.crud.employee import employee_crud
from app.models.attendance import AttendanceCreate, AttendanceUpdate, AttendanceInDB
from app.schemas.attendance import (
    AttendanceListResponse, 
    AttendanceStatsResponse, 
    EmployeeAttendanceReport
)
from app.schemas.common import APIResponse, ErrorResponse, SuccessResponse
from bson import ObjectId, errors as bson_errors

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post(
    "",
    response_model=APIResponse[AttendanceInDB],
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance for an employee",
    description="Mark attendance for a single employee with validation for employee existence and duplicate attendance.",
    responses={
        201: {
            "description": "Attendance marked successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Attendance marked successfully",
                        "data": {
                            "id": "507f1f77bcf86cd799439011",
                            "employee_id": "EMP001",
                            "date": "2024-01-15",
                            "status": "present",
                            "notes": "On time",
                            "marked_by": "Admin",
                            "marked_at": "2024-01-15T09:00:00Z",
                            "created_at": "2024-01-15T09:00:00Z",
                            "updated_at": "2024-01-15T09:00:00Z"
                        },
                        "timestamp": "2024-01-15T09:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Duplicate attendance or invalid date",
            "model": ErrorResponse
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid data format",
            "model": ErrorResponse
        }
    }
)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mark attendance for an employee.
    
    - **employee_id**: Must exist in employees collection
    - **date**: Cannot be in the future
    - **status**: Must be one of: present, absent, half-day, leave
    - **notes**: Optional additional information (max 500 chars)
    - **marked_by**: Person marking the attendance
    """
    try:
        logger.info(f"Marking attendance for employee: {attendance_data.employee_id}")
        
        # Validate date is not in future
        if attendance_data.date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance date cannot be in the future"
            )
        
        # Create attendance (validation handled in CRUD)
        attendance = await attendance_crud.create(db, attendance_data)
        
        logger.info(f"Attendance marked successfully for {attendance_data.employee_id} on {attendance_data.date}")
        return APIResponse(
            data=attendance,
            message="Attendance marked successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error marking attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark attendance"
        )


@router.post(
    "/bulk",
    response_model=APIResponse[List[AttendanceInDB]],
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance for multiple employees",
    description="Mark attendance for multiple employees in a single operation with comprehensive validation.",
    responses={
        201: {
            "description": "Bulk attendance marked successfully"
        },
        400: {
            "description": "Validation error - duplicate attendance or invalid data",
            "model": ErrorResponse
        },
        404: {
            "description": "One or more employees not found",
            "model": ErrorResponse
        }
    }
)
async def bulk_mark_attendance(
    attendance_list: List[AttendanceCreate],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mark attendance for multiple employees.
    
    - **attendance_list**: List of attendance records to create
    - All validations from single attendance apply
    - Returns list of created attendance records
    """
    try:
        logger.info(f"Bulk marking attendance for {len(attendance_list)} employees")
        
        # Validate date is not in future for all records
        for attendance in attendance_list:
            if attendance.date > date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Attendance date cannot be in the future (employee: {attendance.employee_id})"
                )
        
        # Create bulk attendance (validation handled in CRUD)
        created_attendance = await attendance_crud.bulk_mark_attendance(db, attendance_list)
        
        logger.info(f"Bulk attendance marked successfully: {len(created_attendance)} records")
        return APIResponse(
            data=created_attendance,
            message=f"Successfully marked attendance for {len(created_attendance)} employees"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in bulk attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk attendance marking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark bulk attendance"
        )


@router.get(
    "",
    response_model=AttendanceListResponse,
    summary="Get all attendance records with filters",
    description="Retrieve paginated attendance records with optional filtering by employee, date range, status, or department.",
    responses={
        200: {
            "description": "Attendance records retrieved successfully"
        }
    }
)
async def get_attendance(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    status: Optional[str] = Query(None, description="Filter by attendance status"),
    department: Optional[str] = Query(None, description="Filter by employee department"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get attendance records with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (1-100)
    - **employee_id**: Filter by specific employee
    - **start_date**: Filter records from this date onwards
    - **end_date**: Filter records up to this date
    - **status**: Filter by attendance status
    - **department**: Filter by employee department (requires join)
    """
    try:
        logger.info(f"Getting attendance: skip={skip}, limit={limit}, employee_id={employee_id}, start_date={start_date}, end_date={end_date}, status={status}, department={department}")
        
        # Build filter based on parameters
        if start_date and end_date:
            if employee_id:
                attendance = await attendance_crud.get_by_date_range(
                    db, start_date, end_date, employee_id, skip, limit
                )
                total = await attendance_crud.count(db, {
                    "employee_id": employee_id.upper(),
                    "date": {
                        "$gte": datetime.combine(start_date, datetime.min.time()),
                        "$lte": datetime.combine(end_date, datetime.max.time())
                    }
                })
            else:
                attendance = await attendance_crud.get_by_date_range(
                    db, start_date, end_date, None, skip, limit
                )
                total = await attendance_crud.count(db, {
                    "date": {
                        "$gte": datetime.combine(start_date, datetime.min.time()),
                        "$lte": datetime.combine(end_date, datetime.max.time())
                    }
                })
        elif employee_id:
            attendance = await attendance_crud.get_by_employee(db, employee_id, skip, limit)
            total = await attendance_crud.count(db, {"employee_id": employee_id.upper()})
        else:
            # Get all attendance with basic filtering
            filter_query = {}
            if status:
                filter_query["status"] = status
            
            attendance = await attendance_crud.get_multi(db, skip, limit, filter_query)
            total = await attendance_crud.count(db, filter_query)
        
        total_pages = (total + limit - 1) // limit
        
        logger.info(f"Retrieved {len(attendance)} attendance records out of {total} total")
        
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=attendance
        )
        
    except Exception as e:
        logger.error(f"Error getting attendance records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance records"
        )


@router.get(
    "/{id}",
    response_model=APIResponse[AttendanceInDB],
    summary="Get attendance record by ID",
    description="Retrieve a specific attendance record using its MongoDB document ID.",
    responses={
        200: {
            "description": "Attendance record retrieved successfully"
        },
        400: {
            "description": "Invalid ObjectId format",
            "model": ErrorResponse
        },
        404: {
            "description": "Attendance record not found",
            "model": ErrorResponse
        }
    }
)
async def get_attendance_by_id(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get attendance record by MongoDB ObjectId.
    
    - **id**: The MongoDB document ID
    """
    try:
        logger.info(f"Getting attendance by ID: {id}")
        
        attendance = await attendance_crud.get(db, id)
        
        if not attendance:
            logger.warning(f"Attendance not found with ID: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        logger.info(f"Attendance retrieved by ID: {id}")
        return APIResponse(data=attendance)
        
    except ValueError as e:
        logger.warning(f"Invalid ObjectId format: {id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attendance ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance by ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance record"
        )


@router.get(
    "/employee/{employee_id}",
    response_model=AttendanceListResponse,
    summary="Get all attendance for specific employee",
    description="Retrieve all attendance records for a specific employee with optional date filtering.",
    responses={
        200: {
            "description": "Employee attendance retrieved successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        }
    }
)
async def get_employee_attendance(
    employee_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all attendance records for a specific employee.
    
    - **employee_id**: The employee ID to filter by
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (1-100)
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    """
    try:
        logger.info(f"Getting attendance for employee {employee_id}: skip={skip}, limit={limit}, start_date={start_date}, end_date={end_date}")
        
        # Verify employee exists
        employee = await employee_crud.get_by_employee_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        # Get attendance records
        if start_date and end_date:
            attendance = await attendance_crud.get_by_date_range(
                db, start_date, end_date, employee_id, skip, limit
            )
            total = await attendance_crud.count(db, {
                "employee_id": employee_id.upper(),
                "date": {
                    "$gte": datetime.combine(start_date, datetime.min.time()),
                    "$lte": datetime.combine(end_date, datetime.max.time())
                }
            })
        else:
            attendance = await attendance_crud.get_by_employee(db, employee_id, skip, limit)
            total = await attendance_crud.count(db, {"employee_id": employee_id.upper()})
        
        total_pages = (total + limit - 1) // limit
        
        logger.info(f"Retrieved {len(attendance)} attendance records for employee {employee_id}")
        
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=attendance
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee attendance"
        )


@router.get(
    "/date/{date}",
    response_model=AttendanceListResponse,
    summary="Get all attendance for specific date",
    description="Retrieve all attendance records for a specific date. Useful for daily reports.",
    responses={
        200: {
            "description": "Daily attendance retrieved successfully"
        }
    }
)
async def get_daily_attendance(
    date: date,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all attendance records for a specific date.
    
    - **date**: The date to get records for (format: YYYY-MM-DD)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (1-100)
    """
    try:
        logger.info(f"Getting daily attendance for {date}: skip={skip}, limit={limit}")
        
        attendance = await attendance_crud.get_by_date(db, date)
        
        # Apply pagination manually since get_by_date returns all records
        total = len(attendance)
        paginated_attendance = attendance[skip:skip + limit]
        total_pages = (total + limit - 1) // limit
        
        logger.info(f"Retrieved {len(paginated_attendance)} attendance records for {date}")
        
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=paginated_attendance
        )
        
    except Exception as e:
        logger.error(f"Error getting daily attendance for {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily attendance"
        )


@router.put(
    "/{id}",
    response_model=APIResponse[AttendanceInDB],
    summary="Update attendance record",
    description="Update an existing attendance record.",
    responses={
        200: {
            "description": "Attendance updated successfully"
        },
        404: {
            "description": "Attendance record not found",
            "model": ErrorResponse
        }
    }
)
async def update_attendance(
    id: str,
    attendance_data: AttendanceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update attendance record.
    
    - **id**: The MongoDB document ID of the attendance record
    - **attendance_data**: Updated attendance data
    """
    try:
        logger.info(f"Updating attendance record: {id}")
        
        updated_attendance = await attendance_crud.update(db, id, attendance_data)
        
        if not updated_attendance:
            logger.warning(f"Attendance record not found: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        logger.info(f"Attendance updated successfully: {id}")
        return APIResponse(
            data=updated_attendance,
            message="Attendance updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attendance {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attendance"
        )


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Delete attendance record",
    description="Delete an attendance record permanently.",
    responses={
        200: {
            "description": "Attendance deleted successfully"
        },
        404: {
            "description": "Attendance record not found",
            "model": ErrorResponse
        }
    }
)
async def delete_attendance(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete attendance record.
    
    - **id**: The MongoDB document ID of the attendance record
    """
    try:
        logger.info(f"Deleting attendance record: {id}")
        
        deleted = await attendance_crud.delete(db, id)
        
        if not deleted:
            logger.warning(f"Attendance record not found for deletion: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        logger.info(f"Attendance deleted successfully: {id}")
        return SuccessResponse(message="Attendance deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attendance {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attendance"
        )


@router.get(
    "/employee/{employee_id}/summary",
    response_model=APIResponse[EmployeeAttendanceReport],
    summary="Get attendance summary for employee",
    description="Calculate attendance statistics for a specific employee within a date range.",
    responses={
        200: {
            "description": "Attendance summary retrieved successfully"
        },
        404: {
            "description": "Employee not found",
            "model": ErrorResponse
        }
    }
)
async def get_employee_attendance_summary(
    employee_id: str,
    start_date: Optional[date] = Query(None, description="Start date for summary period"),
    end_date: Optional[date] = Query(None, description="End date for summary period"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get attendance summary for an employee.
    
    - **employee_id**: The employee ID to get summary for
    - **start_date**: Optional start date (defaults to first day of current month)
    - **end_date**: Optional end date (defaults to today)
    
    Returns comprehensive attendance statistics including:
    - Total days in period
    - Present/Absent/Half-day/Leave counts
    - Attendance percentage
    """
    try:
        logger.info(f"Getting attendance summary for employee {employee_id}: start_date={start_date}, end_date={end_date}")
        
        # Verify employee exists
        employee = await employee_crud.get_by_employee_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        # Set default dates if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            # Default to first day of current month
            start_date = date(end_date.year, end_date.month, 1)
        
        # Get attendance summary
        summary = await attendance_crud.get_employee_attendance_summary(
            db, employee_id, start_date, end_date
        )
        
        # Create response object
        summary_response = EmployeeAttendanceReport(
            employee_id=employee_id,
            employee_name=employee.full_name,
            total_days=summary["total_days"],
            present_days=summary["present"],
            absent_days=summary["absent"],
            attendance_percentage=summary["attendance_percentage"]
        )
        
        logger.info(f"Attendance summary retrieved for employee {employee_id}")
        return APIResponse(
            data=summary_response,
            message="Attendance summary retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance summary for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance summary"
        )


@router.get(
    "/stats/date/{date}",
    response_model=APIResponse[AttendanceStatsResponse],
    summary="Get attendance statistics for specific date",
    description="Calculate overall attendance statistics for a specific date.",
    responses={
        200: {
            "description": "Daily statistics retrieved successfully"
        }
    }
)
async def get_daily_attendance_stats(
    date: date,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get attendance statistics for a specific date.
    
    - **date**: The date to get statistics for (format: YYYY-MM-DD)
    
    Returns overall attendance statistics including:
    - Total employees marked
    - Count by status (present, absent, half-day, leave)
    - Overall attendance rate
    """
    try:
        logger.info(f"Getting daily attendance stats for {date}")
        
        stats = await attendance_crud.get_attendance_stats_by_date(db, date)
        
        # Create response object
        stats_response = AttendanceStatsResponse(
            total_records=stats["total_employees"],
            present_count=stats["present"],
            absent_count=stats["absent"],
            half_day_count=stats["half_day"],
            leave_count=stats["leave"],
            attendance_rate=stats["attendance_rate"],
            date_range={"start_date": date, "end_date": date}
        )
        
        logger.info(f"Daily attendance stats retrieved for {date}")
        return APIResponse(
            data=stats_response,
            message="Daily attendance statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting daily attendance stats for {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily attendance statistics"
        )


@router.get(
    "/stats/range",
    response_model=APIResponse[AttendanceStatsResponse],
    summary="Get attendance statistics for date range",
    description="Calculate aggregated attendance statistics across a date range.",
    responses={
        200: {
            "description": "Range statistics retrieved successfully"
        }
    }
)
async def get_range_attendance_stats(
    start_date: date = Query(..., description="Start date for statistics range"),
    end_date: date = Query(..., description="End date for statistics range"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get attendance statistics for a date range.
    
    - **start_date**: Start date for the range (inclusive)
    - **end_date**: End date for the range (inclusive)
    
    Returns aggregated statistics across the date range including:
    - Total attendance records
    - Count by status
    - Overall attendance rate
    """
    try:
        logger.info(f"Getting range attendance stats: {start_date} to {end_date}")
        
        # Get attendance for the date range
        attendance = await attendance_crud.get_by_date_range(db, start_date, end_date)
        
        # Calculate statistics
        total_records = len(attendance)
        present_count = sum(1 for a in attendance if a.status == "present")
        absent_count = sum(1 for a in attendance if a.status == "absent")
        half_day_count = sum(1 for a in attendance if a.status == "half-day")
        leave_count = sum(1 for a in attendance if a.status == "leave")
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        # Create response object
        stats_response = AttendanceStatsResponse(
            total_records=total_records,
            present_count=present_count,
            absent_count=absent_count,
            half_day_count=half_day_count,
            leave_count=leave_count,
            attendance_rate=round(attendance_rate, 2),
            date_range={"start_date": start_date, "end_date": end_date}
        )
        
        logger.info(f"Range attendance stats retrieved: {start_date} to {end_date}")
        return APIResponse(
            data=stats_response,
            message="Range attendance statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting range attendance stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve range attendance statistics"
        )


@router.get("/employee/{employee_id}/stats", response_model=AttendanceStats)
async def get_employee_attendance_stats(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
    date_to: Optional[datetime] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get attendance statistics for a specific employee"""
    stats = await attendance_crud.get_employee_stats(db, employee_id, date_from, date_to)
    return stats
