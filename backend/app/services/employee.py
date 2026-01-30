import logging
from typing import Optional, List, Dict, Any, Type
from pymongo.errors import DuplicateKeyError
from app.services.base import BaseRepository
from app.models.employee import EmployeeInDB

logger = logging.getLogger(__name__)


class EmployeeRepository(BaseRepository[EmployeeInDB]):
    
    def __init__(self) -> None:
        super().__init__(collection_name="employees")
    
    @property
    def model_class(self) -> Type[EmployeeInDB]:
        return EmployeeInDB

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
                filter_query["_id"] = {"$ne": exclude_id}
            
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
                filter_query["_id"] = {"$ne": exclude_id}
            
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

    async def get_department_stats(self, db: Any) -> Dict[str, int]:
        try:
            pipeline = [
                {"$group": {"_id": "$department", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            cursor = db[self.collection_name].aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {result["_id"]: result["count"] for result in results}
            
        except Exception as e:
            logger.error(f"Error getting department stats: {e}")
            raise


    async def create(self, db: Any, obj_in: EmployeeInDB) -> EmployeeInDB:
        return await super().create(db, obj_in)

    async def update(
        self,
        db: Any,
        id: str,
        obj_in: EmployeeInDB
    ) -> Optional[EmployeeInDB]:
        try:
            current_employee = await self.get(db, id)
            if not current_employee:
                return None
            
            update_data = obj_in.dict(exclude_unset=True)
            
            if "email" in update_data:
                if await self.check_email_exists(db, update_data["email"], exclude_id=id):
                    raise ValueError(f"Email {update_data['email']} already exists")
                update_data["email"] = update_data["email"].lower()
            
            if "employee_id" in update_data:
                if await self.check_employee_id_exists(db, update_data["employee_id"], exclude_id=id):
                    raise ValueError(f"Employee ID {update_data['employee_id']} already exists")
                update_data["employee_id"] = update_data["employee_id"].upper()
            
            return await super().update(db, id, update_data)
            
        except ValueError:
            raise
        except DuplicateKeyError as e:
            error_msg = str(e)
            if "employee_id" in error_msg:
                raise ValueError("Employee ID already exists")
            elif "email" in error_msg:
                raise ValueError("Email already exists")
            else:
                raise ValueError("Duplicate entry detected")
        except Exception as e:
            logger.error(f"Error updating employee {id}: {e}")
            raise

    async def get_employee_stats(self, db: Any) -> Dict[str, Any]:
        try:
            total_employees = await self.count(db)
            department_stats = await self.get_department_stats(db)
            
            return {
                "total_employees": total_employees,
                "active_employees": 0,
                "inactive_employees": 0,
                "on_leave_employees": 0,
                "department_breakdown": department_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting employee stats: {e}")
            raise


# Create singleton instance
employee_repository = EmployeeRepository()
