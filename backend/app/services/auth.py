from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from app.services.password import verify_password, hash_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        return None

def create_api_key(user_id: str, name: str = "API Key") -> tuple:
    """Generate an API key"""
    import secrets
    import hashlib
    
    # Generate random key
    raw_key = secrets.token_urlsafe(32)
    full_key = f"sk_prod_{raw_key}"
    
    # Hash it for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Keep prefix for user reference
    key_prefix = full_key[:20]
    
    return full_key, key_hash, key_prefix