from contextlib import asynccontextmanager
import logging
import time
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection, check_database_health
from app.api.v1.router import api_router
from app.middleware.error_handler import add_exception_handlers
from app.middleware.cors import setup_cors

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hrms_api.log') if settings.LOG_LEVEL.upper() != 'DEBUG' else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID for tracing"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request processing time"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.4f}s (Request ID: {getattr(request.state, 'request_id', 'unknown')})"
            )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting HRMS Lite API...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("Successfully connected to MongoDB")
        
        # Log application configuration
        logger.info(f"Application: {settings.PROJECT_NAME} v{settings.VERSION}")
   
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown
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
        
        # Calculate uptime (simplified - in production, you'd track actual start time)
        uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        
        health_status = {
            "status": "healthy" if database_status == "healthy" else "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": settings.ENVIRONMENT,
            "database": database_status,
            "uptime": round(uptime, 2)
        }
        
        # Return appropriate status code
        status_code = 200 if database_status == "healthy" else 503
        
        return Response(
            content=str(health_status),
            status_code=status_code,
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "database": "error"
        }
        
        return Response(
            content=str(error_response),
            status_code=503,
            media_type="application/json"
        )


# Store start time for uptime calculation
@app.on_event("startup")
async def store_start_time():
    """Store application start time for uptime calculations"""
    app.state.start_time = time.time()
    logger.info("Application start time recorded")


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
