from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId
from app.core.exceptions import DuplicateError, NotFoundError, ValidationError
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def log_error(level: str, message: str, exc_info: bool = False):
    """
    Log error messages with appropriate log level.
    
    Python's logging module is thread-safe and non-blocking, so async wrapper
    is not necessary. This function provides a consistent logging interface.
    
    Args:
        level: Log level ("error", "warning", or "info")
        message: Log message
        exc_info: Whether to include exception traceback (for error level)
    """
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
        # Log errors
        log_error(
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
        # Log errors
        log_error(
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
        # Log errors
        log_error(
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
        # Log errors
        log_error(
            "warning",
            f"Request validation error - {request.method} {request.url.path}: "
            f"{len(exc.errors())} validation errors"
        )
        
        errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(x) for x in error["loc"])
            
            # Safely serialize input and ctx values
            input_val = error.get("input")
            ctx_val = error.get("ctx")
            
            # Convert to JSON-serializable format
            try:
                input_serializable = str(input_val) if input_val is not None else None
            except Exception:
                input_serializable = "[Non-serializable input]"
                
            try:
                ctx_serializable = str(ctx_val) if ctx_val is not None else None
            except Exception:
                ctx_serializable = "[Non-serializable context]"
            
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": input_serializable,
                "ctx": ctx_serializable
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
        # Log errors
        log_error(
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
        # Log errors
        log_error(
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
        # Log errors with full stack trace
        log_error(
            "error",
            f"Unhandled exception - {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            exc_info=True
        )
        
        # Include request ID if available
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Sanitize error details based on environment
        if not settings.DEBUG:
            error_message = "Internal server error"
        else:
            try:
                error_message = f"{type(exc).__name__}: {str(exc)}"
            except Exception:
                error_message = f"{type(exc).__name__}: [Error details not serializable]"
        
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
