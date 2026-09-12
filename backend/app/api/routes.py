from fastapi import APIRouter
from app.api.auth import router as auth_router

router = APIRouter(prefix="/api/v1", tags=["api"])

# Include auth routes
from app.api import auth

@router.get("/hello")
async def hello():
    """Test endpoint"""
    return {"message": "Hello from SentriGate AI!"}

@router.post("/test-request")
async def test_request(request: dict):
    """Test request processing"""
    return {
        "received": request,
        "status": "processed",
        "threat_score": 0.0
    }