from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.api.deps import get_database_dependency
from app.services.attendance import attendance_repository
from app.models.attendance import AttendanceCreate, AttendanceInDB
from app.schemas.attendance import (
    AttendanceListItem,
    AttendanceListResponse,
    EmployeeAttendanceStatsResponse,
)
from app.schemas.common import APIResponse
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _date_range_filter(start_date: date, end_date: date) -> dict:
    """MongoDB date filter for start_date..end_date inclusive."""
    return {
        "date": {
            "$gte": datetime.combine(start_date, datetime.min.time()),
            "$lte": datetime.combine(end_date, datetime.max.time()),
        }
    }


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
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance already exists for this employee on this date.",
        )
    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error marking attendance: {e}")
        msg = e.errors()[0].get("msg", str(e)) if e.errors() else str(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    except Exception as e:
        logger.exception("Error marking attendance")
        detail = str(e) if str(e).strip() else "Failed to mark attendance"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


@router.get(
    "",
    response_model=AttendanceListResponse,
    response_model_by_alias=False,
)
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
        # Resolve employee_id (code or MongoDB _id) to ObjectId so list matches attendance collection
        resolved_employee_oid = None
        if employee_id:
            try:
                resolved_employee_oid = await attendance_repository.resolve_employee_oid(db, employee_id)
            except ValueError:
                # Employee not found: return empty list
                return AttendanceListResponse(total=0, page=1, page_size=limit, total_pages=0, data=[])
            employee_id_for_repo = str(resolved_employee_oid)

        if start_date and end_date:
            date_filter = _date_range_filter(start_date, end_date)
            if employee_id:
                attendance = await attendance_repository.get_by_date_range(db, start_date, end_date, employee_id_for_repo, skip, limit)
                total = await attendance_repository.count(db, {"employee_id": resolved_employee_oid, **date_filter})
            else:
                attendance = await attendance_repository.get_by_date_range(db, start_date, end_date, None, skip, limit)
                total = await attendance_repository.count(db, date_filter)
        elif employee_id:
            attendance = await attendance_repository.get_by_employee(db, employee_id_for_repo, skip, limit)
            total = await attendance_repository.count(db, {"employee_id": resolved_employee_oid})
        else:
            filter_query = {}
            if status:
                filter_query["status"] = status
            attendance = await attendance_repository.get_multi(db, skip, limit, filter_query)
            total = await attendance_repository.count(db, filter_query)
        
        total_pages = (total + limit - 1) // limit
        data = [AttendanceListItem.from_attendance(a) for a in attendance]
        return AttendanceListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=data,
        )
        
    except Exception as e:
        logger.error(f"Error getting attendance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attendance records")


@router.get(
    "/employee/{employee_id}/stats",
    response_model=APIResponse[EmployeeAttendanceStatsResponse],
)
async def get_employee_attendance_stats(
    employee_id: str,
    start_date: date = Query(..., description="Range start (e.g. month first day)"),
    end_date: date = Query(..., description="Range end (e.g. month last day)"),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency),
):
    """Optimized: single aggregation for one employee's stats in date range."""
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )
        stats = await attendance_repository.get_employee_attendance_stats(
            db, employee_id, start_date, end_date
        )
        return APIResponse(
            data=EmployeeAttendanceStatsResponse(**stats),
            message="Employee attendance statistics retrieved successfully",
        )
    except HTTPException:
        raise
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            f"Error getting employee attendance stats for {employee_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee attendance statistics",
        )


