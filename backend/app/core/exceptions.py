from fastapi import HTTPException, status


class DuplicateError(Exception):
    """Exception for duplicate resource errors"""
    
    def __init__(self, field_name: str, field_value: str, resource_type: str = "Resource"):
        self.field_name = field_name
        self.field_value = field_value
        self.resource_type = resource_type
        message = f"{resource_type} with {field_name} '{field_value}' already exists"
        super().__init__(message)


class NotFoundError(Exception):
    """Exception for resource not found errors"""
    
    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        message = f"{resource_type} with identifier '{identifier}' not found"
        super().__init__(message)


class ValidationError(Exception):
    """Exception for custom validation errors"""
    
    def __init__(self, field_name: str, error_message: str):
        self.field_name = field_name
        self.error_message = error_message
        message = f"Validation error for field '{field_name}': {error_message}"
        super().__init__(message)


class HRMSException(Exception):
    """Base HRMS exception"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DuplicateEmployeeError(HRMSException):
    """Raised when trying to create a duplicate employee"""
    pass


class DuplicateAttendanceError(HRMSException):
    """Raised when trying to create duplicate attendance record"""
    pass


class EmployeeNotFoundError(HRMSException):
    """Raised when employee is not found"""
    pass


class AttendanceNotFoundError(HRMSException):
    """Raised when attendance record is not found"""
    pass


class DatabaseError(HRMSException):
    """Raised when database operation fails"""
    pass


# HTTP Exception helpers
def create_http_exception(status_code: int, detail: str) -> HTTPException:
    """Create HTTP exception with consistent format"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": True,
            "message": detail,
            "status_code": status_code
        }
    )


def not_found_error(resource: str) -> HTTPException:
    """Create 404 not found error"""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def conflict_error(message: str) -> HTTPException:
    """Create 409 conflict error"""
    return create_http_exception(
        status_code=status.HTTP_409_CONFLICT,
        detail=message
    )


def bad_request_error(message: str) -> HTTPException:
    """Create 400 bad request error"""
    return create_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def internal_server_error(message: str = "Internal server error") -> HTTPException:
    """Create 500 internal server error"""
    return create_http_exception(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )
