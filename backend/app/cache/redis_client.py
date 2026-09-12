# app/cache/redis_client.py
import redis
from app.config import settings

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30
)

async def get_redis():
    try:
        yield redis_client
    except redis.ConnectionError:
        raise HTTPException(status_code=500, detail="Cache unavailable")