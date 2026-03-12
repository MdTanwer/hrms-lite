import logging
from typing import Optional, List, Any, Type, Dict
from bson import ObjectId
from app.services.base import BaseRepository
from app.models.employee import EmployeeInDB

logger = logging.getLogger(__name__)


class EmployeeRepository(BaseRepository[EmployeeInDB]):
    
    def __init__(self) -> None:
        super().__init__(collection_name="employees")
    
    @property
    def model_class(self) -> Type[EmployeeInDB]:
        return EmployeeInDB

    @staticmethod
    def build_list_filter(
        search: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build MongoDB filter for list endpoint: optional search and/or department."""
        conditions = []
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
        if not conditions:
            return {}
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    async def get_by_employee_id(
        self, 
        db: Any, 
        employee_id: str
    ) -> Optional[EmployeeInDB]:
        try:
            return await self.get_by_filter(
                db, 
                {"employee_id": employee_id.upper()}
            )
        except Exception as e:
            logger.error(f"Error getting employee by employee_id {employee_id}: {e}")
            raise

    async def get_by_email(
        self, 
        db: Any, 
        email: str
    ) -> Optional[EmployeeInDB]:
        try:
            return await self.get_by_filter(
                db, 
                {"email": email.lower()}
            )
        except Exception as e:
            logger.error(f"Error getting employee by email {email}: {e}")
            raise

    async def check_employee_id_exists(
        self, 
        db: Any, 
        employee_id: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        try:
            filter_query = {"employee_id": employee_id.upper()}
            if exclude_id:
                filter_query["_id"] = {"$ne": ObjectId(exclude_id)}
            
            return await self.exists(db, filter_query)
        except Exception as e:
            logger.error(f"Error checking employee_id existence {employee_id}: {e}")
            raise

    async def check_email_exists(
        self, 
        db: Any, 
        email: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        try:
            filter_query = {"email": email.lower()}
            if exclude_id:
                filter_query["_id"] = {"$ne": ObjectId(exclude_id)}
            
            return await self.exists(db, filter_query)
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            raise

    async def get_by_department(
        self, 
        db: Any, 
        department: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeInDB]:
        try:
            filter_query = {"department": department}
            sort_query = [("full_name", 1)]
            
            return await self.get_multi(
                db,
                skip=skip,
                limit=limit,
                filter_query=filter_query,
                sort_query=sort_query
            )
        except Exception as e:
            logger.error(f"Error getting employees by department {department}: {e}")
            raise


    async def search_employees(
        self,
        db: Any,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeInDB]:
        try:
            regex_pattern = f".*{search_term}.*"
            filter_query = {
                "$or": [
                    {"full_name": {"$regex": regex_pattern, "$options": "i"}},
                    {"email": {"$regex": regex_pattern, "$options": "i"}},
                    {"employee_id": {"$regex": regex_pattern, "$options": "i"}},
                    {"position": {"$regex": regex_pattern, "$options": "i"}}
                ]
            }
            
            sort_query = [("full_name", 1)]
            
            return await self.get_multi(
                db,
                skip=skip,
                limit=limit,
                filter_query=filter_query,
                sort_query=sort_query
            )
        except Exception as e:
            logger.error(f"Error searching employees with term {search_term}: {e}")
            raise

    async def create(self, db: Any, obj_in: EmployeeInDB) -> EmployeeInDB:
        return await super().create(db, obj_in)


# Create singleton instance
employee_repository = EmployeeRepository()
