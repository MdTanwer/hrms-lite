from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db
from app.schemas.employee import EmployeeStats
from app.schemas.attendance import AttendanceStats, DailyAttendanceStats
from app.crud.employee import employee_crud
from app.crud.attendance import attendance_crud

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get complete dashboard overview with employee and attendance statistics"""
    # Get employee statistics
    employee_stats = await employee_crud.get_stats(db)
    
    # Get today's attendance statistics
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_attendance = await attendance_crud.get_daily_stats(db, today_start, today_end)
    
    # Get recent activities (last 5 attendance records)
    recent_activities = await attendance_crud.get_recent_activities(db, limit=5)
    
    return {
        "employee_stats": employee_stats,
        "today_attendance": today_attendance,
        "recent_activities": recent_activities
    }


@router.get("/attendance/daily", response_model=DailyAttendanceStats)
async def get_daily_attendance_stats(
    target_date: Optional[date] = Query(None, description="Target date for attendance stats"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get daily attendance statistics for a specific date"""
    if target_date is None:
        target_date = date.today()
    
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())
    
    stats = await attendance_crud.get_daily_stats(db, day_start, day_end)
    return stats


@router.get("/attendance/summary")
async def get_attendance_summary(
    date_from: Optional[date] = Query(None, description="Start date for summary"),
    date_to: Optional[date] = Query(None, description="End date for summary"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get attendance summary for a date range"""
    if date_from is None:
        date_from = date.today().replace(day=1)  # First day of current month
    if date_to is None:
        date_to = date.today()
    
    start_datetime = datetime.combine(date_from, datetime.min.time())
    end_datetime = datetime.combine(date_to, datetime.max.time())
    
    summary = await attendance_crud.get_attendance_summary(db, start_datetime, end_datetime)
    return summary


@router.get("/department/attendance")
async def get_department_attendance_stats(
    target_date: Optional[date] = Query(None, description="Target date for department stats"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get attendance statistics broken down by department"""
    if target_date is None:
        target_date = date.today()
    
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())
    
    stats = await attendance_crud.get_department_attendance_stats(db, day_start, day_end)
    return stats
