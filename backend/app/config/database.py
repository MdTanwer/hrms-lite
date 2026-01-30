import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config.settings import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Create MongoDB connection with connection pooling and index creation"""
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
        
        # Create indexes for better performance
        await create_indexes()
        
        logger.info("MongoDB indexes created successfully")
        
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
    """Close MongoDB connection"""
    try:
        if mongodb.client is not None:
            mongodb.client.close()
            logger.info("Disconnected from MongoDB successfully")
        else:
            logger.warning("No MongoDB client to close")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency function to get database instance"""
    if mongodb.database is None:
        raise ConnectionError("Database not initialized. Call connect_to_mongo() first.")
    return mongodb.database


async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Employees collection indexes
        await mongodb.database.employees.create_index(
            "employee_id",
            unique=True,
            name="employee_id_unique_index"
        )
        await mongodb.database.employees.create_index(
            "email",
            unique=True,
            name="email_unique_index"
        )
        await mongodb.database.employees.create_index(
            "department",
            name="department_index"
        )
        await mongodb.database.employees.create_index(
            "status",
            name="status_index"
        )
        await mongodb.database.employees.create_index(
            [("full_name", "text"), ("position", "text")],
            name="search_index"
        )
        
        # Attendance collection indexes
        await mongodb.database.attendance.create_index(
            [("employee_id", 1), ("date", 1)],
            unique=True,
            name="employee_date_unique_index"
        )
        await mongodb.database.attendance.create_index(
            "date",
            name="date_index"
        )
        await mongodb.database.attendance.create_index(
            "status",
            name="status_index"
        )
        await mongodb.database.attendance.create_index(
            "marked_at",
            name="marked_at_index"
        )
        
        logger.info("All MongoDB indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")
        raise


async def check_database_health() -> dict:
    """Check MongoDB connection health"""
    try:
        if mongodb.client is None:
            return {"status": "unhealthy", "message": "No MongoDB client"}
        
        # Ping the database
        await mongodb.client.admin.command('ping')
        
        # Get server info
        server_info = await mongodb.client.server_info()
        
        # Get database stats
        db_stats = await mongodb.database.command("dbStats")
        
        return {
            "status": "healthy",
            "version": server_info.get("version"),
            "database": settings.MONGODB_DB_NAME,
            "collections": db_stats.get("collections", 0),
            "data_size": db_stats.get("dataSize", 0),
            "indexes": db_stats.get("indexes", 0)
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }
