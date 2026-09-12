from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import json

class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate requests before processing
    """
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing"""
        
        # Skip validation for GET requests and non-JSON endpoints
        if request.method == "GET":
            return await call_next(request)
        
        # Check Content-Type for POST, PUT, PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if not content_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content-Type header is required"
                )
            
            if "application/json" not in content_type:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Content-Type must be application/json"
                )
            
            # Check Content-Length
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    length = int(content_length)
                    max_size = 1024 * 1024  # 1MB
                    if length > max_size:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Payload too large. Max size is {max_size} bytes"
                        )
                except ValueError:
                    pass
        
        # Continue to next middleware
        response = await call_next(request)
        return response


class PayloadValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate request payload size
    """
    
    async def dispatch(self, request: Request, call_next):
        """Check payload size"""
        
        if request.method in ["POST", "PUT", "PATCH"]:
            # Read body
            body = await request.body()
            
            # Check size (1MB limit)
            max_size = 1024 * 1024
            if len(body) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request payload exceeds maximum size of {max_size} bytes"
                )
            
            # Try to parse JSON to validate format
            if body:
                try:
                    json.loads(body)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid JSON payload"
                    )
        
        response = await call_next(request)
        return response