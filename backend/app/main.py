from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import models FIRST
from app.models.user import User
from app.models.api_key import APIKey
from app.models.role import Role
from app.models.permission import Permission
from app.models.associations import UserRole, RolePermission

# Import database and create tables
from app.database import Base, engine
Base.metadata.create_all(bind=engine)

# Import routes
from app.api import auth

# Import middleware
from app.middleware.rate_limit import rate_limit_middleware

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Secure API Gateway with ML-powered threat detection",
    version="1.0.0"
)

# Add rate limiting middleware FIRST (before CORS)
app.middleware("http")(rate_limit_middleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth.router)

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "SentriGate AI API Security Gateway",
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

@app.get("/api/v1/status")
async def api_status():
    return {
        "service": "Security Gateway",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )