import logging
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId
from app.core.exceptions import DuplicateError, NotFoundError, ValidationError
from app.config.settings import settings

logger = logging.getLogger(__name__)


async def log_error_async(level: str, message: str, exc_info: bool = False):
    """Async logging to prevent blocking request processing"""
    if level == "error":
        logger.error(message, exc_info=exc_info)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)


def add_exception_handlers(app: FastAPI):
    """Add custom exception handlers to the FastAPI application"""
    
    @app.exception_handler(DuplicateError)
    async def duplicate_error_handler(request: Request, exc: DuplicateError):
        """Handle duplicate resource errors"""
        # Log errors asynchronously to prevent blocking
        await log_error_async(
            "warning",
            f"Duplicate error - {request.method} {request.url.path}: "
            f"{exc.field_name}='{exc.field_value}' for {exc.resource_type}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": str(exc),
                "error_type": "duplicate_error",
                "field": exc.field_name,
                "value": exc.field_value,
                "resource_type": exc.resource_type,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        """Handle resource not found errors"""
        # Log errors asynchronously
        await log_error_async(
            "warning",
            f"Not found error - {request.method} {request.url.path}: "
            f"{exc.resource_type} with identifier '{exc.identifier}'"
        )
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": str(exc),
                "error_type": "not_found",
                "resource_type": exc.resource_type,
                "identifier": exc.identifier,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle custom validation errors"""
        # Log errors asynchronously
        await log_error_async(
            "warning",
            f"Validation error - {request.method} {request.url.path}: "
            f"Field '{exc.field_name}': {exc.error_message}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": str(exc),
                "error_type": "validation_error",
                "field": exc.field_name,
                "error_message": exc.error_message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors"""
        # Log errors asynchronously
        await log_error_async(
            "warning",
            f"Request validation error - {request.method} {request.url.path}: "
            f"{len(exc.errors())} validation errors"
        )
        
        errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(x) for x in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
                "ctx": error.get("ctx")
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation error",
                "error_type": "request_validation_error",
                "errors": errors,
                "error_count": len(errors),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(InvalidId)
    async def invalid_object_id_handler(request: Request, exc: InvalidId):
        """Handle invalid MongoDB ObjectId errors"""
        # Log errors asynchronously
        await log_error_async(
            "warning",
            f"Invalid ObjectId error - {request.method} {request.url.path}: "
            f"Invalid ID format: {str(exc)}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Invalid ID format",
                "error_type": "invalid_id",
                "details": "The provided ID is not a valid MongoDB ObjectId format",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_error_handler(request: Request, exc: DuplicateKeyError):
        """Handle MongoDB duplicate key errors"""
        # Log errors asynchronously
        await log_error_async(
            "warning",
            f"Duplicate key error - {request.method} {request.url.path}: "
            f"Database constraint violation: {str(exc)}"
        )
        
        # Extract field information from error message more robustly
        error_message = str(exc)
        field_info = "unknown"
        
        # Common MongoDB duplicate key patterns
        field_patterns = {
            "email": ["email", "email_address"],
            "employee_id": ["employee_id", "emp_id", "employee"],
            "username": ["username", "user_name"],
            "phone": ["phone", "phone_number", "mobile"]
        }
        
        for field, patterns in field_patterns.items():
            if any(pattern in error_message.lower() for pattern in patterns):
                field_info = field
                break
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Duplicate entry detected",
                "error_type": "duplicate_key_error",
                "field": field_info,
                "details": "A record with this value already exists",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other unhandled exceptions"""
        # Log errors asynchronously with full stack trace
        await log_error_async(
            "error",
            f"Unhandled exception - {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            exc_info=True
        )
        
        # Include request ID if available
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Sanitize error details based on environment
        error_message = "Internal server error" if not settings.DEBUG else str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": error_message,
                "error_type": "server_error",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


def setup_error_handlers(app):
    """Setup error handlers for the FastAPI app (legacy - use add_exception_handlers instead)"""
    # This function is deprecated. Use add_exception_handlers(app) instead.
    # Keeping for backward compatibility but recommend migration.
    pass
