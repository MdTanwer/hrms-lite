import logging
from typing import Optional, List, Dict, Any, Type, Union
from datetime import date, datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError
from app.services.base import BaseRepository
from app.models.attendance import AttendanceInDB
from app.services.employee import employee_repository

logger = logging.getLogger(__name__)


def _is_objectid(s: str) -> bool:
    """True if s is a valid 24-char hex MongoDB ObjectId string."""
    if not s or len(s) != 24:
        return False
    try:
        ObjectId(s)
        return True
    except (InvalidId, TypeError):
        return False


def _normalize_employee_id_for_filter(employee_id: str) -> Union[ObjectId, str]:
    """Return ObjectId or str for MongoDB filter; DB stores employee_id as ObjectId."""
    if _is_objectid(employee_id):
        return ObjectId(employee_id)
    return employee_id.upper()


def _date_range_bounds(start_date: date, end_date: date) -> tuple:
    """Return (start_datetime, end_datetime) for inclusive MongoDB date filter."""
    return (
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time()),
    )


class AttendanceRepository(BaseRepository[AttendanceInDB]):
    def __init__(self) -> None:
        super().__init__(collection_name="attendance")
    
    @property
    def model_class(self) -> Type[AttendanceInDB]:
        return AttendanceInDB

    async def check_attendance_exists(self, db: Any, employee_id: str, att_date: date) -> bool:
        try:
            start_dt, end_dt = _date_range_bounds(att_date, att_date)
            filter_query = {
                "employee_id": _normalize_employee_id_for_filter(employee_id),
                "date": {"$gte": start_dt, "$lte": end_dt},
            }
            return await self.exists(db, filter_query)
        except Exception as e:
            logger.error(f"Error checking attendance existence: {e}")
            raise

    async def get_by_employee(self, db: Any, employee_id: str, skip: int = 0, limit: int = 100) -> List[AttendanceInDB]:
        try:
            filter_query = {"employee_id": _normalize_employee_id_for_filter(employee_id)}
            sort_query = [("date", 1)]  # ascending: 1st, 2nd, 3rd... of month
            return await self.get_multi(db, skip=skip, limit=limit, filter_query=filter_query, sort_query=sort_query)
        except Exception as e:
            logger.error(f"Error getting attendance for employee {employee_id}: {e}")
            raise

    async def get_by_date_range(self, db: Any, start_date: date, end_date: date, employee_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[AttendanceInDB]:
        try:
            start_dt, end_dt = _date_range_bounds(start_date, end_date)
            filter_query = {"date": {"$gte": start_dt, "$lte": end_dt}}
            if employee_id:
                filter_query["employee_id"] = _normalize_employee_id_for_filter(employee_id)
            sort_query = [("date", 1)]  # ascending: 1st, 2nd, 3rd... of month
            return await self.get_multi(db, skip=skip, limit=limit, filter_query=filter_query, sort_query=sort_query)
        except Exception as e:
            logger.error(f"Error getting attendance by date range: {e}")
            raise

    @staticmethod
    def _working_days_in_range(start_date: date, end_date: date) -> int:
        """Count weekdays (Mon–Fri) between start_date and end_date inclusive."""
        from datetime import timedelta
        count = 0
        d = start_date
        while d <= end_date:
            if d.weekday() < 5:  # 0=Mon .. 4=Fri
                count += 1
            d += timedelta(days=1)
        return count

    async def resolve_employee_oid(self, db: Any, employee_id: str) -> ObjectId:
        """Resolve employee_id (MongoDB _id string or employee code) to ObjectId used in attendance collection."""
        if _is_objectid(employee_id):
            return ObjectId(employee_id)
        employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        return ObjectId(employee.id)

    async def get_employee_attendance_stats(
        self, db: Any, employee_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """
        Single aggregation: employee stats (present/absent/half-day/leave) in date range.

        total_days: Working days (Mon–Fri) in range — used as denominator so rate is
        "attendance vs expected days". Half-days count as 0.5 toward effective presence.
        Division-by-zero: if total_days == 0 or total_recorded == 0, rate is 0.0.
        """
        try:
            emp_oid = await self.resolve_employee_oid(db, employee_id)
            start_dt, end_dt = _date_range_bounds(start_date, end_date)
            total_days = self._working_days_in_range(start_date, end_date)
            pipeline = [
                {
                    "$match": {
                        "employee_id": emp_oid,
                        "date": {"$gte": start_dt, "$lte": end_dt},
                    }
                },
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            ]
            cursor = db[self.collection_name].aggregate(pipeline)
            results = await cursor.to_list(length=10)
            present_days = absent_days = half_days = leave_days = 0
            for r in results:
                c = r["count"]
                if r["_id"] == "present":
                    present_days = c
                elif r["_id"] == "absent":
                    absent_days = c
                elif r["_id"] == "half-day":
                    half_days = c
                elif r["_id"] == "leave":
                    leave_days = c
            # Rate: effective_present (present=1, half-day=0.5) / total_days. Alternative:
            # denominator = total_recorded (present+absent+half_days+leave_days) if you
            # prefer "rate among days with a record" instead of "rate vs expected working days".
            effective_present = present_days + 0.5 * half_days
            denominator = total_days
            attendance_rate = (
                round((effective_present / denominator) * 100, 2)
                if denominator and denominator > 0
                else 0.0
            )
            return {
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "half_days": half_days,
                "leave_days": leave_days,
                "attendance_rate": attendance_rate,
            }
        except Exception as e:
            logger.error(f"Error getting employee attendance stats for {employee_id}: {e}")
            raise

    async def create(self, db: Any, obj_in: AttendanceInDB) -> AttendanceInDB:
        try:
            if await self.check_attendance_exists(db, obj_in.employee_id, obj_in.date):
                raise ValueError(f"Attendance already exists for employee {obj_in.employee_id} on {obj_in.date}")

            if _is_objectid(obj_in.employee_id):
                employee = await employee_repository.get(db, obj_in.employee_id)
            else:
                employee = await employee_repository.get_by_employee_id(db, obj_in.employee_id)
            if not employee:
                raise ValueError(f"Employee {obj_in.employee_id} not found")

            emp_oid = ObjectId(employee.id)
            now_utc = datetime.now(timezone.utc)
            date_dt = datetime.combine(obj_in.date, datetime.min.time())
            # Insert with employee_id as ObjectId (model_dump() would serialize it as str)
            doc = {
                "employee_id": emp_oid,
                "date": date_dt,
                "status": obj_in.status or "present",
                "notes": obj_in.notes,
                "marked_by": getattr(obj_in, "marked_by", "Admin"),
                "marked_at": now_utc,
                "created_at": now_utc,
                "updated_at": now_utc,
            }
            result = await db[self.collection_name].insert_one(doc)
            created_doc = await db[self.collection_name].find_one({"_id": result.inserted_id})
            if not created_doc:
                raise PyMongoError("Failed to retrieve created attendance document")
            return self.model_class(**created_doc)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating attendance: {e}")
            raise


attendance_repository = AttendanceRepository()
