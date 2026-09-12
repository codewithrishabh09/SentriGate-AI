# app/schemas/request.py
from pydantic import BaseModel, Field, validator
from typing import Dict, Any

class APIRequest(BaseModel):
    endpoint: str = Field(..., max_length=500)
    method: str = Field(..., regex="^(GET|POST|PUT|DELETE|PATCH)$")
    payload: Dict[str, Any] = Field(..., max_length=100000)  # Max 100KB
    headers: Dict[str, str] = Field(default={}, max_length=50)
    
    @validator('payload')
    def validate_payload_size(cls, v):
        if len(str(v)) > 100000:
            raise ValueError('Payload exceeds max size')
        return v