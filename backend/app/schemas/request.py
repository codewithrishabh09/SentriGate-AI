from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from app.utils.sanitizer import sanitize_dict

class APIRequest(BaseModel):
    """Schema for API requests with validation"""
    
    endpoint: str = Field(..., max_length=500)
    method: str = Field(..., regex="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    
    @validator('endpoint')
    def validate_endpoint(cls, v):
        """Validate endpoint format"""
        if not v.startswith('/'):
            raise ValueError('Endpoint must start with /')
        if '..' in v or '//' in v:
            raise ValueError('Invalid endpoint path')
        return v
    
    @validator('payload')
    def sanitize_payload(cls, v):
        """Sanitize payload data"""
        if v:
            v = sanitize_dict(v)
        return v


class ThreatAnalysisRequest(BaseModel):
    """Request for threat analysis"""
    
    url: str = Field(..., max_length=2000)
    method: str = Field(default="GET", regex="^(GET|POST|PUT|DELETE)$")
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = Field(None, max_length=10000)
    
    @validator('body')
    def validate_body_size(cls, v):
        """Validate body size"""
        if v and len(v.encode()) > 10000:
            raise ValueError('Request body exceeds maximum size')
        return v