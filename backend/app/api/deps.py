import logging
from typing import AsyncGenerator

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError

from app.config.database import get_database as get_db_connection

logger = logging.getLogger(__name__)


async def get_database_dependency() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency function to inject database connection into route handlers.

    Yields:
        AsyncIOMotorDatabase: MongoDB database instance

    Raises:
        HTTPException: If database connection is unavailable
    """
    try:
        database = await get_db_connection()
        if database is None:
            logger.error("Database connection failed - database is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable",
            )
        logger.debug("Database dependency injected successfully")
        yield database
    except HTTPException:
        raise
    except (RequestValidationError, ValidationError):
        raise  # Let FastAPI validation handler return 422 with proper message
    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Database dependency error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        )


