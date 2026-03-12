from contextlib import asynccontextmanager
import time
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.logging_config import get_logger
from app.config.database import connect_to_mongo, close_mongo_connection, check_database_health
from app.api.v1.router import api_router
from app.middleware import (
    add_exception_handlers,
    setup_cors,
    RequestIDMiddleware,
    RequestTimingMiddleware,
)

# Get logger instance
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting HRMS Lite API...")
    startup_successful = False
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("Successfully connected to MongoDB")
        
        # Store start time for uptime calculation
        app.state.start_time = time.time()
        logger.info("Application start time recorded")
        
        # Log application configuration
        logger.info(f"Application: {settings.PROJECT_NAME} v{settings.VERSION}")
        
        startup_successful = True
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown (only if startup was successful)
    if startup_successful:
        logger.info("Shutting down HRMS Lite API...")
        
        try:
            # Close MongoDB connection
            await close_mongo_connection()
            logger.info("Successfully disconnected from MongoDB")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestTimingMiddleware)

# Configure CORS using the dedicated setup function
setup_cors(app)

# Add custom exception handlers
add_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get(
    "/",
    summary="Root endpoint",
    responses={
        200: {
            "description": "Welcome message with API information",
        }
    }
)
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns welcome message with useful navigation links.
    """
    return {
        "message": "Welcome to HRMS Lite API",
        "version": settings.VERSION,
    }


@app.get(
    "/health",
    summary="Health check endpoint",
    responses={
        200: {
            "description": "System is healthy",
        },
        503: {
            "description": "System is unhealthy",
        }
    }
)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    """
    try:
        # Check database connectivity
        db_health = await check_database_health()
        database_status = db_health["status"]
        
        # Calculate uptime
        uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        
        health_status = {
            "status": "healthy" if database_status == "healthy" else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "environment": settings.ENVIRONMENT,
            "database": database_status,
            "uptime": round(uptime, 2)
        }
        
        # Return appropriate status code
        status_code = 200 if database_status == "healthy" else 503
        
        return JSONResponse(
            content=health_status,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "error": str(e),
            "database": "error"
        }
        
        return JSONResponse(
            content=error_response,
            status_code=503
        )


# Log application startup
logger.info(f"FastAPI application '{settings.PROJECT_NAME}' initialized")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
