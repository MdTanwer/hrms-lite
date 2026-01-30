import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.crud.base import CRUDBase
from app.models.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB

logger = logging.getLogger(__name__)


class EmployeeCRUD(CRUDBase[EmployeeInDB, EmployeeCreate, EmployeeUpdate]):
    """
    CRUD operations for Employee documents.
    
    Extends the base CRUD class with employee-specific operations.
    """
    
    def __init__(self):
        """Initialize EmployeeCRUD with employees collection."""
        super().__init__(collection_name="employees")
    
    @property
    def model_class(self):
        """Return the EmployeeInDB model class."""
        return EmployeeInDB

    async def get_by_employee_id(
        self, 
        db: AsyncIOMotorDatabase, 
        employee_id: str
    ) -> Optional[EmployeeInDB]:
        """
        Get employee by employee_id field.
        
        Args:
            db: MongoDB database instance
            employee_id: Employee ID to search for
            
        Returns:
            Employee instance if found, None otherwise
        """
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
        db: AsyncIOMotorDatabase, 
        email: str
    ) -> Optional[EmployeeInDB]:
        """
        Get employee by email (case-insensitive).
        
        Args:
            db: MongoDB database instance
            email: Email address to search for
            
        Returns:
            Employee instance if found, None otherwise
        """
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
        db: AsyncIOMotorDatabase, 
        employee_id: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if employee_id already exists.
        
        Args:
            db: MongoDB database instance
            employee_id: Employee ID to check
            exclude_id: Exclude this employee ID from check (for updates)
            
        Returns:
            True if employee_id exists, False otherwise
        """
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
        db: AsyncIOMotorDatabase, 
        email: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if email already exists (case-insensitive).
        
        Args:
            db: MongoDB database instance
            email: Email address to check
            exclude_id: Exclude this employee ID from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
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
        db: AsyncIOMotorDatabase, 
        department: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeInDB]:
        """
        Get employees filtered by department.
        
        Args:
            db: MongoDB database instance
            department: Department name to filter by
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of employees in the department
        """
        try:
            filter_query = {"department": department}
            sort_query = [("full_name", 1)]  # Sort by name
            
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

    async def get_by_status(
        self, 
        db: AsyncIOMotorDatabase, 
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeInDB]:
        """
        Get employees filtered by status.
        
        Args:
            db: MongoDB database instance
            status: Status to filter by
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of employees with the specified status
        """
        try:
            filter_query = {"status": status}
            sort_query = [("full_name", 1)]  # Sort by name
            
            return await self.get_multi(
                db,
                skip=skip,
                limit=limit,
                filter_query=filter_query,
                sort_query=sort_query
            )
        except Exception as e:
            logger.error(f"Error getting employees by status {status}: {e}")
            raise

    async def search_employees(
        self,
        db: AsyncIOMotorDatabase,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeInDB]:
        """
        Search employees across multiple fields.
        
        Args:
            db: MongoDB database instance
            search_term: Term to search for
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of matching employees
        """
        try:
            # Create case-insensitive regex search
            regex_pattern = f".*{search_term}.*"
            filter_query = {
                "$or": [
                    {"full_name": {"$regex": regex_pattern, "$options": "i"}},
                    {"email": {"$regex": regex_pattern, "$options": "i"}},
                    {"employee_id": {"$regex": regex_pattern, "$options": "i"}},
                    {"position": {"$regex": regex_pattern, "$options": "i"}}
                ]
            }
            
            sort_query = [("full_name", 1)]  # Sort by name
            
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

    async def get_department_stats(
        self,
        db: AsyncIOMotorDatabase
    ) -> Dict[str, int]:
        """
        Get employee count by department using aggregation.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with department counts
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$department",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            cursor = db[self.collection_name].aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Convert to simple dict
            department_stats = {
                result["_id"]: result["count"] 
                for result in results
            }
            
            logger.debug(f"Department stats: {department_stats}")
            return department_stats
            
        except Exception as e:
            logger.error(f"Error getting department stats: {e}")
            raise

    async def get_recent_hires(
        self,
        db: AsyncIOMotorDatabase,
        days: int = 30,
        limit: int = 5
    ) -> List[EmployeeInDB]:
        """
        Get recently hired employees.
        
        Args:
            db: MongoDB database instance
            days: Number of days to look back
            limit: Maximum number of employees to return
            
        Returns:
            List of recently hired employees
        """
        try:
            # Calculate the date N days ago
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            filter_query = {
                "start_date": {"$gte": cutoff_date}
            }
            
            sort_query = [("start_date", -1)]  # Most recent first
            
            return await self.get_multi(
                db,
                skip=0,
                limit=limit,
                filter_query=filter_query,
                sort_query=sort_query
            )
        except Exception as e:
            logger.error(f"Error getting recent hires from last {days} days: {e}")
            raise

    async def create(self, db: AsyncIOMotorDatabase, obj_in: EmployeeCreate) -> EmployeeInDB:
        """
        Create a new employee with validation.
        
        Args:
            db: MongoDB database instance
            obj_in: Employee creation data
            
        Returns:
            Created employee instance
            
        Raises:
            ValueError: If employee_id or email already exists
        """
        try:
            # Check for duplicate employee_id
            if await self.check_employee_id_exists(db, obj_in.employee_id):
                raise ValueError(f"Employee ID {obj_in.employee_id} already exists")
            
            # Check for duplicate email
            if await self.check_email_exists(db, obj_in.email):
                raise ValueError(f"Email {obj_in.email} already exists")
            
            # Convert email to lowercase for consistency
            obj_in_data = obj_in.dict()
            obj_in_data["email"] = obj_in_data["email"].lower()
            obj_in_data["employee_id"] = obj_in_data["employee_id"].upper()
            
            # Create the employee using parent method
            return await super().create(db, obj_in_data)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating employee: {e}")
            raise

    async def update(
        self,
        db: AsyncIOMotorDatabase,
        id: str,
        obj_in: EmployeeUpdate
    ) -> Optional[EmployeeInDB]:
        """
        Update an employee with validation.
        
        Args:
            db: MongoDB database instance
            id: Employee document ID
            obj_in: Employee update data
            
        Returns:
            Updated employee instance if found, None otherwise
            
        Raises:
            ValueError: If email or employee_id already exists (if being updated)
        """
        try:
            # Get current employee for validation
            current_employee = await self.get(db, id)
            if not current_employee:
                return None
            
            # Convert to dict for validation
            update_data = obj_in.dict(exclude_unset=True)
            
            # Validate email uniqueness if being updated
            if "email" in update_data:
                if await self.check_email_exists(db, update_data["email"], exclude_id=id):
                    raise ValueError(f"Email {update_data['email']} already exists")
                update_data["email"] = update_data["email"].lower()
            
            # Validate employee_id uniqueness if being updated
            if "employee_id" in update_data:
                if await self.check_employee_id_exists(db, update_data["employee_id"], exclude_id=id):
                    raise ValueError(f"Employee ID {update_data['employee_id']} already exists")
                update_data["employee_id"] = update_data["employee_id"].upper()
            
            # Update the employee using parent method
            return await super().update(db, id, update_data)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating employee {id}: {e}")
            raise

    async def get_employee_stats(
        self,
        db: AsyncIOMotorDatabase
    ) -> Dict[str, Any]:
        """
        Get comprehensive employee statistics.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with employee statistics
        """
        try:
            # Get total counts
            total_employees = await self.count(db)
            
            # Get status breakdown
            status_pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            status_cursor = db[self.collection_name].aggregate(status_pipeline)
            status_results = await status_cursor.to_list(length=None)
            
            status_counts = {
                result["_id"]: result["count"] 
                for result in status_results
            }
            
            # Get department stats
            department_stats = await self.get_department_stats(db)
            
            # Get average salary
            salary_pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "average_salary": {"$avg": "$salary"}
                    }
                }
            ]
            
            salary_cursor = db[self.collection_name].aggregate(salary_pipeline)
            salary_result = await salary_cursor.to_list(length=1)
            average_salary = salary_result[0]["average_salary"] if salary_result else 0
            
            # Get recent hires
            recent_hires = await self.get_recent_hires(db, days=30, limit=5)
            
            stats = {
                "total_employees": total_employees,
                "active_employees": status_counts.get("active", 0),
                "inactive_employees": status_counts.get("inactive", 0),
                "on_leave_employees": status_counts.get("on-leave", 0),
                "department_breakdown": department_stats,
                "average_salary": round(average_salary, 2),
                "recent_hires": recent_hires
            }
            
            logger.debug(f"Employee stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting employee stats: {e}")
            raise


# Create singleton instance
employee_crud = EmployeeCRUD()
