from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.utils.sanitizer import sanitize_string, validate_username

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('username')
    def validate_username_format(cls, v):
        """Validate username format"""
        if not validate_username(v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('full_name')
    def sanitize_full_name(cls, v):
        """Sanitize full name"""
        if v:
            v = sanitize_string(v, max_length=255)
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


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
    
    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize API key name"""
        return sanitize_string(v, max_length=100)


class APIKeyResponse(BaseModel):
    api_key_id: str
    key: str
    key_prefix: str
    name: str
    status: str
    created_at: datetime