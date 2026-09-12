import redis
from app.config import settings
from typing import Optional

# Create Redis connection
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30
)

def get_redis():
    """FastAPI dependency for Redis"""
    try:
        yield redis_client
    except redis.ConnectionError:
        yield None