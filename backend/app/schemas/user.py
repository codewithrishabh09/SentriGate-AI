from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    full_name: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class APIKeyGenerate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    rate_limit_requests: int = Field(default=1000, ge=1, le=100000)
    rate_limit_window_seconds: int = Field(default=3600, ge=60, le=86400)

class APIKeyResponse(BaseModel):
    api_key_id: str
    key: str
    key_prefix: str
    name: str
    status: str
    created_at: datetime