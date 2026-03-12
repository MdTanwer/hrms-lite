import logging
from typing import Optional, List, Dict, Any, Type
from datetime import date, datetime
from app.services.base import BaseRepository
from app.models.attendance import AttendanceInDB
from app.services.employee import employee_repository

logger = logging.getLogger(__name__)


class AttendanceRepository(BaseRepository[AttendanceInDB]):
    def __init__(self) -> None:
        super().__init__(collection_name="attendance")
    
    @property
    def model_class(self) -> Type[AttendanceInDB]:
        return AttendanceInDB

    async def check_attendance_exists(self, db: Any, employee_id: str, date: date) -> bool:
        try:
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            filter_query = {
                "employee_id": employee_id.upper(),
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }
            return await self.exists(db, filter_query)
        except Exception as e:
            logger.error(f"Error checking attendance existence: {e}")
            raise

    async def get_by_employee(self, db: Any, employee_id: str, skip: int = 0, limit: int = 100) -> List[AttendanceInDB]:
        try:
            filter_query = {"employee_id": employee_id.upper()}
            sort_query = [("date", -1)]
            return await self.get_multi(db, skip=skip, limit=limit, filter_query=filter_query, sort_query=sort_query)
        except Exception as e:
            logger.error(f"Error getting attendance for employee {employee_id}: {e}")
            raise

    async def get_by_date_range(self, db: Any, start_date: date, end_date: date, employee_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[AttendanceInDB]:
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            filter_query = {"date": {"$gte": start_datetime, "$lte": end_datetime}}
            if employee_id:
                filter_query["employee_id"] = employee_id.upper()
            sort_query = [("date", -1)]
            return await self.get_multi(db, skip=skip, limit=limit, filter_query=filter_query, sort_query=sort_query)
        except Exception as e:
            logger.error(f"Error getting attendance by date range: {e}")
            raise

    async def get_by_date(self, db: Any, date: date) -> List[AttendanceInDB]:
        try:
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            filter_query = {"date": {"$gte": start_datetime, "$lte": end_datetime}}
            sort_query = [("marked_at", -1)]
            return await self.get_multi(db, skip=0, limit=1000, filter_query=filter_query, sort_query=sort_query)
        except Exception as e:
            logger.error(f"Error getting attendance for date {date}: {e}")
            raise

    async def get_attendance_stats_by_date(self, db: Any, date: date) -> Dict[str, Any]:
        try:
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            pipeline = [
                {"$match": {"date": {"$gte": start_datetime, "$lte": end_datetime}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            cursor = db[self.collection_name].aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            stats = {"total_employees": 0, "present": 0, "absent": 0, "half_day": 0, "leave": 0, "attendance_rate": 0.0}
            
            for result in results:
                status = result["_id"]
                count = result["count"]
                stats["total_employees"] += count
                
                if status == "present":
                    stats["present"] = count
                elif status == "absent":
                    stats["absent"] = count
                elif status == "half-day":
                    stats["half_day"] = count
                elif status == "leave":
                    stats["leave"] = count
            
            if stats["total_employees"] > 0:
                stats["attendance_rate"] = round((stats["present"] / stats["total_employees"]) * 100, 2)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting attendance stats by date: {e}")
            raise

    async def get_employee_attendance_summary(self, db: Any, employee_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        try:
            match_stage: Dict[str, Any] = {}
            match_stage["employee_id"] = employee_id.upper()
            
            if start_date or end_date:
                date_filter: Dict[str, Any] = {}
                if start_date:
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                    date_filter["$gte"] = start_datetime
                if end_date:
                    end_datetime = datetime.combine(end_date, datetime.max.time())
                    date_filter["$lte"] = end_datetime
                match_stage["date"] = date_filter
            
            pipeline = [{"$match": match_stage}, {"$group": {"_id": "$status", "count": {"$sum": 1}}}]
            cursor = db[self.collection_name].aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            stats = {"total_days": 0, "present": 0, "absent": 0, "half_day": 0, "leave": 0, "attendance_percentage": 0.0}
            
            for result in results:
                status = result["_id"]
                count = result["count"]
                stats["total_days"] += count
                
                if status == "present":
                    stats["present"] = count
                elif status == "absent":
                    stats["absent"] = count
                elif status == "half-day":
                    stats["half_day"] = count
                elif status == "leave":
                    stats["leave"] = count
            
            if stats["total_days"] > 0:
                effective_present = stats["present"] + (stats["half_day"] * 0.5)
                stats["attendance_percentage"] = round((effective_present / stats["total_days"]) * 100, 2)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting employee attendance summary: {e}")
            raise


    async def create(self, db: Any, obj_in: AttendanceInDB) -> AttendanceInDB:
        try:
            if await self.check_attendance_exists(db, obj_in.employee_id, obj_in.date):
                raise ValueError(f"Attendance already exists for employee {obj_in.employee_id} on {obj_in.date}")
            
            employee = await employee_repository.get_by_employee_id(db, obj_in.employee_id)
            if not employee:
                raise ValueError(f"Employee {obj_in.employee_id} not found")
            
            # MongoDB BSON cannot encode datetime.date; use datetime at midnight UTC
            patch = {
                "employee_id": obj_in.employee_id.upper(),
                "date": datetime.combine(obj_in.date, datetime.min.time()),
                "marked_at": datetime.utcnow(),
            }
            try:
                obj_to_create = obj_in.copy(update=patch)
            except AttributeError:
                obj_to_create = obj_in.model_copy(update=patch)
            return await super().create(db, obj_to_create)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating attendance: {e}")
            raise


attendance_repository = AttendanceRepository()
