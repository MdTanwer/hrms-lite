from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.services.employee import employee_repository
from app.models.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB
from app.schemas.employee import EmployeeListResponse, EmployeeStatsResponse
from app.schemas.common import APIResponse, SuccessResponse
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=APIResponse[EmployeeInDB], status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        existing_employee = await employee_repository.get_by_employee_id(db, employee_data.employee_id)
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with ID {employee_data.employee_id} already exists"
            )
        
        existing_by_email = await employee_repository.get_by_email(db, employee_data.email)
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email {employee_data.email} already exists"
            )
        
        employee = await employee_repository.create(db, employee_data)
        
        return APIResponse(
            data=employee,
            message="Employee created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee"
        )


@router.get("", response_model=EmployeeListResponse)
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        if search:
            employees = await employee_repository.search_employees(db, search, skip, limit)
            total = await employee_repository.count(db, {
                "$or": [
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"employee_id": {"$regex": search, "$options": "i"}},
                    {"position": {"$regex": search, "$options": "i"}}
                ]
            })
        elif department:
            employees = await employee_repository.get_by_department(db, department, skip, limit)
            total = await employee_repository.count(db, {"department": department})
        elif status:
            employees = await employee_repository.get_by_status(db, status, skip, limit)
            total = await employee_repository.count(db, {"status": status})
        else:
            employees = await employee_repository.get_multi(db, skip, limit)
            total = await employee_repository.count(db)
        
        total_pages = (total + limit - 1) // limit
        
        return EmployeeListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=employees
        )
    except Exception as e:
        logger.error(f"Error getting employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employees"
        )


@router.get("/{employee_id}", response_model=APIResponse[EmployeeInDB])
async def get_employee_by_id(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        employee = await employee_repository.get_by_employee_id(db, employee_id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        return APIResponse(data=employee)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee"
        )


@router.get("/id/{id}", response_model=APIResponse[EmployeeInDB])
async def get_employee_by_object_id(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        employee = await employee_repository.get(db, id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        return APIResponse(data=employee)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee by ObjectId {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee"
        )


@router.put("/{employee_id}", response_model=APIResponse[EmployeeInDB])
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        current_employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        updated_employee = await employee_repository.update(db, str(current_employee.id), employee_data)
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        return APIResponse(
            data=updated_employee,
            message="Employee updated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )


@router.patch("/{employee_id}", response_model=APIResponse[EmployeeInDB])
async def partial_update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        current_employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        updated_employee = await employee_repository.update(db, str(current_employee.id), employee_data)
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        return APIResponse(
            data=updated_employee,
            message="Employee updated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error partially updating employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )


@router.delete("/{employee_id}", response_model=SuccessResponse)
async def delete_employee(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        current_employee = await employee_repository.get_by_employee_id(db, employee_id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found"
            )
        
        attendance_count = await db["attendance"].count_documents({"employee_id": employee_id.upper()})
        if attendance_count > 0:
            update_data = EmployeeUpdate(status="inactive")
            await employee_repository.update(db, str(current_employee.id), update_data)
            message = f"Employee {employee_id} deactivated (soft delete due to attendance records)"
        else:
            await employee_repository.delete(db, str(current_employee.id))
            message = f"Employee {employee_id} deleted successfully"
        
        return SuccessResponse(message=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee"
        )


@router.get("/department/{department}", response_model=EmployeeListResponse)
async def get_employees_by_department(
    department: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        employees = await employee_repository.get_by_department(db, department, skip, limit)
        total = await employee_repository.count(db, {"department": department})
        total_pages = (total + limit - 1) // limit
        
        return EmployeeListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            data=employees
        )
    except Exception as e:
        logger.error(f"Error getting employees by department {department}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employees by department"
        )


@router.get("/stats", response_model=APIResponse[EmployeeStatsResponse])
async def get_employee_stats(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        stats = await employee_repository.get_employee_stats(db)
        
        stats_response = EmployeeStatsResponse(
            total_employees=stats["total_employees"],
            active_employees=stats["active_employees"],
            inactive_employees=stats["inactive_employees"],
            on_leave_employees=stats["on_leave_employees"],
            department_breakdown=stats["department_breakdown"],
            average_salary=stats["average_salary"],
            recent_hires=stats["recent_hires"]
        )
        
        return APIResponse(
            data=stats_response,
            message="Employee statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting employee statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee statistics"
        )
