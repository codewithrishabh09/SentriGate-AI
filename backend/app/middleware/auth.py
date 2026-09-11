# app/middleware/auth.py
from fastapi import Depends, HTTPException, status
from app.services.auth import verify_token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": user_id}

async def require_permission(permission: str):
    async def permission_checker(current_user = Depends(get_current_user)):
        # Check if user has permission
        if not has_permission(current_user["user_id"], permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker