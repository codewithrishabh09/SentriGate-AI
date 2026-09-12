import redis
from datetime import datetime, timedelta
from typing import Tuple
import time

def check_rate_limit(
    redis_client: redis.Redis,
    api_key: str,
    limit: int,
    window_seconds: int
) -> Tuple[bool, dict]:
    """
    Sliding window rate limiter using Redis ZSET
    
    Returns: (allowed: bool, info: dict)
    """
    
    if not redis_client:
        # If Redis is down, allow request
        return True, {"remaining": limit, "reset_at": None}
    
    try:
        key = f"rate_limit:{api_key}"
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Remove requests outside the window
        redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        request_count = redis_client.zcard(key)
        
        # Check if limit exceeded
        allowed = request_count < limit
        remaining = max(0, limit - request_count - (1 if allowed else 0))
        
        if allowed:
            # Add current request timestamp
            redis_client.zadd(key, {str(current_time): current_time})
            # Set expiration to window size + buffer
            redis_client.expire(key, window_seconds + 1)
        
        # Get oldest request in window for reset time
        oldest = redis_client.zrange(key, 0, 0, withscores=True)
        reset_at = None
        if oldest:
            reset_at = int(oldest[0][1]) + window_seconds
        
        return allowed, {
            "remaining": remaining,
            "limit": limit,
            "reset_at": reset_at,
            "window_seconds": window_seconds
        }
    
    except Exception as e:
        # If Redis fails, allow request (fail open)
        print(f"Rate limit check error: {e}")
        return True, {"remaining": limit, "reset_at": None}


def get_rate_limit_config(redis_client: redis.Redis, api_key: str, db=None) -> dict:
    """
    Get rate limit config for an API key from cache or database
    """
    
    if not redis_client:
        return {"requests_per_minute": 60, "requests_per_hour": 3600}
    
    try:
        # Try to get from cache first
        cached = redis_client.get(f"rl_config:{api_key}")
        if cached:
            import json
            return json.loads(cached)
    except:
        pass
    
    # If not cached or Redis down, return defaults
    return {
        "requests_per_minute": 60,
        "requests_per_hour": 3600
    }