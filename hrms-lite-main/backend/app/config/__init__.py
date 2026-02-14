"""
Configuration module for HRMS Lite API.

This module provides centralized configuration for:
- Application settings (environment, database, CORS, etc.)
- Logging configuration
- Database connection management

Common imports:
    from app.config import settings, get_logger
    from app.config import connect_to_mongo, close_mongo_connection
"""

# Import settings - most commonly used
from app.config.settings import settings

# Import logging utilities
from app.config.logging_config import get_logger, setup_logging

# Import database utilities
from app.config.database import (
    connect_to_mongo,
    close_mongo_connection,
    check_database_health,
    get_database,
)

__all__ = [
    # Settings
    "settings",
    # Logging
    "get_logger",
    "setup_logging",
    # Database
    "connect_to_mongo",
    "close_mongo_connection",
    "check_database_health",
    "get_database",
]