import logging
from datetime import datetime, timezone
from typing import Optional, List, Any, Type, Dict
from bson import ObjectId
from pymongo.errors import PyMongoError

from app.services.base import BaseRepository
from app.models.employee import EmployeeInDB

logger = logging.getLogger(__name__)

# Exclude soft-deleted employees from all list/get operations
NOT_DELETED = {"$or": [{"deleted_at": {"$exists": False}}, {"deleted_at": None}]}


class EmployeeRepository(BaseRepository[EmployeeInDB]):
    def __init__(self) -> None:
        super().__init__(collection_name="employees")

    @property
    def model_class(self) -> Type[EmployeeInDB]:
        return EmployeeInDB

    @staticmethod
    def _and_not_deleted(filter_query: Dict[str, Any]) -> Dict[str, Any]:
        """Merge filter with NOT_DELETED so soft-deleted employees are excluded."""
        if not filter_query:
            return NOT_DELETED
        return {"$and": [NOT_DELETED, filter_query]}

    @staticmethod
    def build_list_filter(
        search: Optional[str] = None,
        department: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build MongoDB filter for list endpoint; always excludes soft-deleted."""
        conditions = [NOT_DELETED]
        if department:
            conditions.append({"department": department})
        if search and search.strip():
            regex_pattern = f".*{search.strip()}.*"
            conditions.append({
                "$or": [
                    {"full_name": {"$regex": regex_pattern, "$options": "i"}},
                    {"email": {"$regex": regex_pattern, "$options": "i"}},
                    {"employee_id": {"$regex": regex_pattern, "$options": "i"}},
                    {"position": {"$regex": regex_pattern, "$options": "i"}},
                ]
            })
        return {"$and": conditions} if len(conditions) > 1 else conditions[0]

    async def get(self, db: Any, id: str) -> Optional[EmployeeInDB]:
        """Get by _id; returns None if not found or soft-deleted."""
        try:
            object_id = ObjectId(id)
        except (Exception, TypeError):
            return None
        try:
            doc = await db[self.collection_name].find_one(
                {"$and": [{"_id": object_id}, NOT_DELETED]}
            )
            return self.model_class(**doc) if doc else None
        except PyMongoError as e:
            logger.error(f"Error getting employee {id}: {e}")
            raise

    async def get_by_employee_id(
        self,
        db: Any,
        employee_id: str,
    ) -> Optional[EmployeeInDB]:
        try:
            return await self.get_by_filter(
                db,
                self._and_not_deleted({"employee_id": employee_id.upper()}),
            )
        except Exception as e:
            logger.error(f"Error getting employee by employee_id {employee_id}: {e}")
            raise

    async def get_by_email(
        self,
        db: Any,
        email: str,
    ) -> Optional[EmployeeInDB]:
        try:
            return await self.get_by_filter(
                db,
                self._and_not_deleted({"email": email.lower()}),
            )
        except Exception as e:
            logger.error(f"Error getting employee by email {email}: {e}")
            raise

    async def get_by_department(
        self,
        db: Any,
        department: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[EmployeeInDB]:
        try:
            filter_query = self._and_not_deleted({"department": department})
            sort_query = [("full_name", 1)]
            return await self.get_multi(
                db,
                skip=skip,
                limit=limit,
                filter_query=filter_query,
                sort_query=sort_query,
            )
        except Exception as e:
            logger.error(f"Error getting employees by department {department}: {e}")
            raise

    async def soft_delete(self, db: Any, employee_id: str) -> bool:
        """Soft delete: set deleted_at (and updated_at). Returns True if updated."""
        employee = await self.get_by_employee_id(db, employee_id)
        if not employee:
            return False
        now = datetime.now(timezone.utc)
        try:
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(employee.id)},
                {"$set": {"deleted_at": now, "updated_at": now}},
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error soft-deleting employee {employee_id}: {e}")
            raise

    async def create(self, db: Any, obj_in: EmployeeInDB) -> EmployeeInDB:
        return await super().create(db, obj_in)


# Create singleton instance
employee_repository = EmployeeRepository()
