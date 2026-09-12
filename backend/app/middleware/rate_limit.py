# app/middleware/rate_limit.py
from app.cache.redis_client import redis_client
from time import time

async def rate_limit_check(api_key: str, limit: int = 100, window: int = 3600):
    """Sliding window rate limiting"""
    key = f"rate_limit:{api_key}"
    current_time = int(time())
    window_start = current_time - window
    
    # Remove old requests
    redis_client.zremrangebyscore(key, 0, window_start)
    
    # Count requests in window
    request_count = redis_client.zcard(key)
    
    if request_count >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    redis_client.zadd(key, {str(current_time): current_time})
    redis_client.expire(key, window + 1)
    
    return {"remaining": limit - request_count - 1}