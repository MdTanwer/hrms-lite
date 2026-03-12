"""Employee management API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_database_dependency
from app.models.employee import EmployeeCreate, EmployeeInDB
from app.schemas.common import APIResponse, SuccessResponse
from app.schemas.employee import EmployeeListResponse
from app.services.employee import employee_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=APIResponse[EmployeeInDB], status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
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


@router.get(
    "",
    response_model=EmployeeListResponse,
    response_model_by_alias=False,
)
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
):
    try:
        # Build filter for backend: search and/or department (no client-side filtering)
        filter_query = employee_repository.build_list_filter(search=search, department=department)
        employees = await employee_repository.get_multi(
            db, skip=skip, limit=limit,
            filter_query=filter_query,
            sort_query=[("created_at", -1)]  # latest first
        )
        total = await employee_repository.count(db, filter_query)
        total_pages = (total + limit - 1) // limit if limit else 0

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


@router.get(
    "/department/{department}",
    response_model=EmployeeListResponse,
    response_model_by_alias=False,
)
async def get_employees_by_department(
    department: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
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


@router.get("/{employee_id}", response_model=APIResponse[EmployeeInDB])
async def get_employee_by_id(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency)
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


@router.delete("/{employee_id}", response_model=SuccessResponse)
async def delete_employee(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database_dependency),
):
    """Soft delete: sets deleted_at so the employee is hidden from lists and lookups."""
    try:
        updated = await employee_repository.soft_delete(db, employee_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found",
            )
        return SuccessResponse(message=f"Employee {employee_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee",
        )
