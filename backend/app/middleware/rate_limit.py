from fastapi import Request, HTTPException, status
from app.cache.redis_client import redis_client
from app.services.rate_limiter import check_rate_limit
from app.database import get_db
from app.models.api_key import APIKey
import time

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for all requests
    Checks API key and enforces rate limits
    """
    
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Extract API key from header
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        # If no API key, allow (for auth endpoints)
        response = await call_next(request)
        return response
    
    # Check rate limit (1 minute window, 100 requests)
    allowed, info = check_rate_limit(
        redis_client,
        api_key=api_key,
        limit=100,
        window_seconds=60
    )
    
    if not allowed:
        retry_after = info.get("reset_at")
        if retry_after:
            retry_after = max(0, retry_after - int(time.time()))
        
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after or 60)}
        )
    
    response = await call_next(request)
    
    # Add rate limit info to response headers
    response.headers["X-RateLimit-Limit"] = str(info.get("limit", 100))
    response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
    if info.get("reset_at"):
        response.headers["X-RateLimit-Reset"] = str(info.get("reset_at"))
    
    return response