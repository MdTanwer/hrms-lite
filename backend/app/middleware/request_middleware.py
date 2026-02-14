"""
Request middleware for HRMS Lite API.

This module provides middleware for:
- Request ID tracking for distributed tracing
- Request timing and performance monitoring
"""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.logging_config import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID for tracing.
    
    Adds a unique UUID to each request for distributed tracing and logging.
    The request ID is stored in request.state and added to response headers.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and add unique request ID.
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler in the chain
            
        Returns:
            Response with X-Request-ID header
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request processing time.
    
    Measures request processing time and logs slow requests.
    Adds X-Process-Time header to all responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and measure processing time.
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler in the chain
            
        Returns:
            Response with X-Process-Time header
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add timing header to successful responses
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            # Log slow requests (taking more than 1 second)
            if process_time > 1.0:
                request_id = getattr(request.state, 'request_id', 'unknown')
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} "
                    f"took {process_time:.4f}s (Request ID: {request_id})"
                )
            
            return response
            
        except Exception as e:
            # Calculate time even if request fails (for logging)
            process_time = time.time() - start_time
            
            # Log slow failed requests
            if process_time > 1.0:
                request_id = getattr(request.state, 'request_id', 'unknown')
                logger.warning(
                    f"Slow failed request: {request.method} {request.url.path} "
                    f"took {process_time:.4f}s before failing (Request ID: {request_id})"
                )
            
            # Re-raise exception to be handled by exception handlers
            raise
