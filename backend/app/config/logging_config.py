"""
Logging configuration for HRMS Lite API.

This module provides centralized logging configuration with support for:
- Console logging (always enabled)
- File logging (optional, based on environment)
- Structured logging with proper formatting
- Log rotation for production environments
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

from app.config.settings import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Sets up logging with appropriate handlers based on environment:
    - Development: Console + File logging
    - Production: Console + Rotating file handler
    - DEBUG mode: More verbose console output
    
    Raises:
        OSError: If log directory cannot be created (non-critical, falls back to console only)
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Prevent multiple setups
    if root_logger.handlers and hasattr(root_logger, '_hrms_configured'):
        return
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Validate and set logging level from settings
    log_level_name = settings.LOG_LEVEL.upper()
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    if log_level_name not in valid_levels:
        log_level_name = 'INFO'
        root_logger.warning(
            f"Invalid LOG_LEVEL '{settings.LOG_LEVEL}', defaulting to INFO"
        )
    
    log_level = getattr(logging, log_level_name, logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use detailed formatter in DEBUG mode, simple otherwise
    if settings.DEBUG or settings.LOG_LEVEL.upper() == 'DEBUG':
        console_handler.setFormatter(detailed_formatter)
    else:
        console_handler.setFormatter(simple_formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handler (enabled for all environments except when explicitly in DEBUG mode)
    if log_level_name != 'DEBUG':
        try:
            # Use project root directory for logs (more reliable than os.getcwd())
            # Try to find the backend directory or use current working directory
            current_path = Path(__file__).parent.parent.parent  # Go up from config/logging_config.py to backend/
            log_dir = current_path / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / 'hrms_api.log'
            
            # Use rotating file handler in production
            if settings.ENVIRONMENT == 'production':
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=str(log_file),
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,  # Keep 5 backup files
                    encoding='utf-8'
                )
            else:
                # Regular file handler for staging/development
                file_handler = logging.FileHandler(
                    filename=str(log_file),
                    encoding='utf-8'
                )
            
            file_handler.setLevel(log_level)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
            
            # Use root_logger instead of logging module for consistency
            root_logger.info(f"File logging enabled: {log_file}")
            
        except (OSError, PermissionError) as e:
            # Non-critical: continue with console logging only
            root_logger.warning(
                f"Could not create log file: {e}. "
                "Continuing with console logging only."
            )
    
    # Configure third-party loggers to reduce noise
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    logging.getLogger('motor').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    
    # Mark as configured to prevent re-setup
    root_logger._hrms_configured = True
    
    # Use root_logger instead of logging module for consistency
    root_logger.info(
        f"Logging configured - Level: {log_level_name}, "
        f"Environment: {settings.ENVIRONMENT}"
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__). If None, returns root logger.
    
    Returns:
        Configured logger instance.
    
    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()
