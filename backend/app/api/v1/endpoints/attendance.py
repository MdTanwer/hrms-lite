from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_database_dependency
from app.services.attendance import attendance_repository
from app.services.employee import employee_repository
from app.models.attendance import AttendanceCreate, AttendanceUpdate, AttendanceInDB
from app.schemas.attendance import (
    AttendanceListResponse, 
    AttendanceStatsResponse, 
    EmployeeAttendanceReport
)
from app.models.attendance import AttendanceStats
from app.schemas.common import APIResponse, SuccessResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", response_model=APIResponse[AttendanceInDB], status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        if attendance_data.date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attendance date cannot be in the future")
        
        attendance = await attendance_repository.create(db, attendance_data)
        return APIResponse(data=attendance, message="Attendance marked successfully")
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark attendance")


@router.get("", response_model=AttendanceListResponse)
async def get_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        if start_date and end_date:
            if employee_id:
                attendance = await attendance_repository.get_by_date_range(db, start_date, end_date, employee_id, skip, limit)
                total = await attendance_repository.count(db, {
                    "employee_id": employee_id.upper(),
                    "date": {"$gte": datetime.combine(start_date, datetime.min.time()), "$lte": datetime.combine(end_date, datetime.max.time())}
                })
            else:
                attendance = await attendance_repository.get_by_date_range(db, start_date, end_date, None, skip, limit)
                total = await attendance_repository.count(db, {
                    "date": {"$gte": datetime.combine(start_date, datetime.min.time()), "$lte": datetime.combine(end_date, datetime.max.time())}
                })
        elif employee_id:
            attendance = await attendance_repository.get_by_employee(db, employee_id, skip, limit)
            total = await attendance_repository.count(db, {"employee_id": employee_id.upper()})
        else:
            filter_query = {}
            if status:
                filter_query["status"] = status
            attendance = await attendance_repository.get_multi(db, skip, limit, filter_query)
            total = await attendance_repository.count(db, filter_query)
        
        total_pages = (total + limit - 1) // limit
        
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=attendance
        )
        
    except Exception as e:
        logger.error(f"Error getting attendance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attendance records")


@router.get("/{id}", response_model=APIResponse[AttendanceInDB])
async def get_attendance_by_id(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        attendance = await attendance_repository.get(db, id)
        
        if not attendance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
        
        return APIResponse(data=attendance)
        
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid attendance ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance by ID {id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attendance record")


@router.get("/employee/{employee_id}", response_model=AttendanceListResponse)
async def get_employee_attendance(
    employee_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
        
        if start_date and end_date:
            attendance = await attendance_repository.get_by_date_range(db, start_date, end_date, employee_id, skip, limit)
            total = await attendance_repository.count(db, {
                "employee_id": employee_id.upper(),
                "date": {"$gte": datetime.combine(start_date, datetime.min.time()), "$lte": datetime.combine(end_date, datetime.max.time())}
            })
        else:
            attendance = await attendance_repository.get_by_employee(db, employee_id, skip, limit)
            total = await attendance_repository.count(db, {"employee_id": employee_id.upper()})
        
        total_pages = (total + limit - 1) // limit
        
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve employee attendance")


@router.get("/date/{date}", response_model=AttendanceListResponse)
async def get_daily_attendance(
    date: date,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        attendance = await attendance_repository.get_by_date(db, date)
        
        total = len(attendance)
        paginated_attendance = attendance[skip:skip + limit]
        total_pages = (total + limit - 1) // limit
        
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=paginated_attendance
        )
        
    except Exception as e:
        logger.error(f"Error getting daily attendance for {date}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve daily attendance")


@router.put("/{id}", response_model=APIResponse[AttendanceInDB])
async def update_attendance(
    id: str,
    attendance_data: AttendanceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        updated_attendance = await attendance_repository.update(db, id, attendance_data)
        
        if not updated_attendance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
        
        return APIResponse(data=updated_attendance, message="Attendance updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attendance {id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update attendance")


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_attendance(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        deleted = await attendance_repository.delete(db, id)
        
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
        
        return SuccessResponse(message="Attendance deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attendance {id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete attendance")


@router.get("/employee/{employee_id}/summary", response_model=APIResponse[EmployeeAttendanceReport])
async def get_employee_attendance_summary(
    employee_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = date(end_date.year, end_date.month, 1)
        
        summary = await attendance_repository.get_employee_attendance_summary(db, employee_id, start_date, end_date)
        
        summary_response = EmployeeAttendanceReport(
            employee_id=employee_id,
            employee_name=employee.full_name,
            total_days=summary["total_days"],
            present_days=summary["present"],
            absent_days=summary["absent"],
            attendance_percentage=summary["attendance_percentage"]
        )
        
        return APIResponse(data=summary_response, message="Attendance summary retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance summary for employee {employee_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attendance summary")


@router.get("/stats/date/{date}", response_model=APIResponse[AttendanceStatsResponse])
async def get_daily_attendance_stats(
    date: date,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        stats = await attendance_repository.get_attendance_stats_by_date(db, date)
        
        stats_response = AttendanceStatsResponse(
            total_records=stats["total_employees"],
            present_count=stats["present"],
            absent_count=stats["absent"],
            half_day_count=stats["half_day"],
            leave_count=stats["leave"],
            attendance_rate=stats["attendance_rate"],
            date_range={"start_date": date, "end_date": date}
        )
        
        return APIResponse(data=stats_response, message="Daily attendance statistics retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting daily attendance stats for {date}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve daily attendance statistics")


@router.get("/stats/range", response_model=APIResponse[AttendanceStatsResponse])
async def get_range_attendance_stats(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        attendance = await attendance_repository.get_by_date_range(db, start_date, end_date)
        
        total_records = len(attendance)
        present_count = sum(1 for a in attendance if a.status == "present")
        absent_count = sum(1 for a in attendance if a.status == "absent")
        half_day_count = sum(1 for a in attendance if a.status == "half-day")
        leave_count = sum(1 for a in attendance if a.status == "leave")
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        stats_response = AttendanceStatsResponse(
            total_records=total_records,
            present_count=present_count,
            absent_count=absent_count,
            half_day_count=half_day_count,
            leave_count=leave_count,
            attendance_rate=round(attendance_rate, 2),
            date_range={"start_date": start_date, "end_date": end_date}
        )
        
        return APIResponse(data=stats_response, message="Range attendance statistics retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting range attendance stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve range attendance statistics")


@router.get("/employee/{employee_id}/stats", response_model=AttendanceStats)
async def get_employee_attendance_stats(
    employee_id: str,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        stats = await attendance_repository.get_employee_attendance_summary(db, employee_id, date_from, date_to)
        
        return AttendanceStats(
            total_days=stats["total_days"],
            present_days=stats["present"],
            absent_days=stats["absent"],
            half_day_days=stats["half_day"],
            leave_days=stats["leave"],
            attendance_rate=stats["attendance_percentage"]
        )
    except Exception as e:
        logger.error(f"Error getting employee attendance stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve employee attendance statistics")
