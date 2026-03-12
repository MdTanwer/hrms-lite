from app.config.logging_config import get_logger
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config.settings import settings

logger = get_logger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo():
    """
    Create MongoDB connection with connection pooling and index creation.
    
    Raises:
        ConnectionError: If connection to MongoDB fails
    """
    try:
        # Create AsyncIOMotorClient with connection pooling
        mongodb.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
            minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
            serverSelectionTimeoutMS=5000,  # 5 seconds timeout
            connectTimeoutMS=10000,  # 10 seconds timeout
            retryWrites=True,
            w="majority"
        )
        
        # Get database reference
        mongodb.database = mongodb.client[settings.MONGODB_DB_NAME]
        
        # Test connection with ping
        await mongodb.client.admin.command('ping')
        
        # Get server info for logging
        server_info = await mongodb.client.server_info()
        logger.info(
            f"Connected to MongoDB successfully! "
            f"Version: {server_info.get('version', 'Unknown')}, "
            f"Database: {settings.MONGODB_DB_NAME}"
        )
        
        # Create indexes for better performance (non-blocking if they already exist)
        try:
            await create_indexes()
            logger.info("MongoDB indexes created/verified successfully")
        except Exception as index_error:
            # Log but don't fail connection if index creation fails
            logger.warning(
                f"Failed to create some indexes (non-critical): {index_error}. "
                "Application will continue, but some queries may be slower."
            )
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionError(f"Could not connect to MongoDB: {e}")
    except ServerSelectionTimeoutError as e:
        logger.error(f"MongoDB server selection timeout: {e}")
        raise ConnectionError(f"MongoDB server selection timeout: {e}")
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise ConnectionError(f"Unexpected error connecting to MongoDB: {e}")


async def close_mongo_connection():
    """
    Close MongoDB connection gracefully.
    
    Safely closes the MongoDB client connection and cleans up resources.
    """
    try:
        if mongodb.client is not None:
            mongodb.client.close()
            mongodb.client = None
            mongodb.database = None
            logger.info("Disconnected from MongoDB successfully")
        else:
            logger.warning("No MongoDB client to close")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
        # Ensure cleanup even if close fails
        mongodb.client = None
        mongodb.database = None


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Raises:
        ConnectionError: If database is not initialized
    """
    if mongodb.database is None:
        raise ConnectionError("Database not initialized. Call connect_to_mongo() first.")
    return mongodb.database


async def create_indexes():
    """
    Create database indexes for better performance.
    
    Creates indexes if they don't exist. MongoDB handles duplicate index
    creation gracefully, so this is safe to call multiple times.
    
    Raises:
        Exception: If database is not initialized or index creation fails
    """
    if mongodb.database is None:
        raise ConnectionError("Database not initialized. Cannot create indexes.")
    
    try:
        # Employees collection indexes - only essential ones
        # Unique constraint for employee_id
        await mongodb.database.employees.create_index(
            "employee_id",
            unique=True,
            name="employee_id_unique_index"
        )
        # Unique constraint for email
        await mongodb.database.employees.create_index(
            "email",
            unique=True,
            name="email_unique_index"
        )
        # Department index - used in get_by_department queries
        await mongodb.database.employees.create_index(
            "department",
            name="department_index"
        )
        
        # Attendance collection indexes - only essential ones
        # Unique constraint for employee_id + date combination
        await mongodb.database.attendance.create_index(
            [("employee_id", 1), ("date", 1)],
            unique=True,
            name="employee_date_unique_index"
        )
        # Date index - used in date range queries and sorting
        await mongodb.database.attendance.create_index(
            "date",
            name="date_index"
        )
        # Marked_at index - used in sorting attendance records
        await mongodb.database.attendance.create_index(
            "marked_at",
            name="marked_at_index"
        )
        
        logger.debug("Essential MongoDB indexes created/verified successfully")
        
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")
        raise


async def check_database_health() -> dict:
    """
    Check MongoDB connection health.
    
    Returns:
        dict: Health status with database information
        
    Returns status "unhealthy" if connection check fails, otherwise "healthy"
    """
    try:
        if mongodb.client is None or mongodb.database is None:
            return {
                "status": "unhealthy",
                "message": "MongoDB client or database not initialized"
            }
        
        # Ping the database to verify connection
        await mongodb.client.admin.command('ping')
        
        # Get server info
        server_info = await mongodb.client.server_info()
        
        # Get database stats (may fail if database doesn't exist yet)
        try:
            db_stats = await mongodb.database.command("dbStats")
            return {
                "status": "healthy",
                "version": server_info.get("version"),
                "database": settings.MONGODB_DB_NAME,
                "collections": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "indexes": db_stats.get("indexes", 0)
            }
        except Exception as stats_error:
            # Database exists but stats command failed (non-critical)
            logger.warning(f"Could not get database stats: {stats_error}")
            return {
                "status": "healthy",
                "version": server_info.get("version"),
                "database": settings.MONGODB_DB_NAME,
                "message": "Connection healthy but stats unavailable"
            }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }
