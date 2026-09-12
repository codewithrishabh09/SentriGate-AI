# app/cache/session.py
import json
from datetime import datetime, timedelta

async def create_session(user_id: str, data: dict, redis_client):
    session_id = f"session:{user_id}:{uuid.uuid4()}"
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        **data
    }
    redis_client.setex(
        session_id,
        timedelta(hours=24),
        json.dumps(session_data)
    )
    return session_id

async def get_session(session_id: str, redis_client):
    data = redis_client.get(session_id)
    if not data:
        raise HTTPException(status_code=401, detail="Session expired")
    return json.loads(data)