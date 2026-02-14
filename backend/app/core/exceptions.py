"""Custom exceptions for HRMS application"""


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
