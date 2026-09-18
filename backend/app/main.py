from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import models FIRST
from app.models.user import User
from app.models.api_key import APIKey
from app.models.role import Role
from app.models.permission import Permission
from app.models.associations import UserRole, RolePermission
from app.models.audit import AuditLog, ThreatEvent, SecurityAlert

# Import database
from app.database import Base, engine
Base.metadata.create_all(bind=engine)

# Import middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.validation import ValidationMiddleware, PayloadValidationMiddleware
from app.middleware.threat_detection import threat_detection_middleware
from app.middleware.audit_logging import audit_logging_middleware

# Import routes DIRECTLY (not from __init__.py)
from app.api.auth import router as auth_router
from app.api.audit import router as audit_router

# Create app
app = FastAPI(
    title=settings.app_name,
    description="Secure API Gateway with ML-powered threat detection",
    version="1.0.0"
)

# Middleware order (bottom = first executed)
app.add_middleware(PayloadValidationMiddleware)
app.add_middleware(ValidationMiddleware)
app.middleware("http")(threat_detection_middleware)
app.middleware("http")(audit_logging_middleware)
app.middleware("http")(rate_limit_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(audit_router)

@app.get("/")
async def root():
    return {
        "message": "SentriGate AI API Security Gateway",
        "status": "operational",
        "environment": settings.environment,
        "security_features": [
            "Rate Limiting (Redis)",
            "Input Validation",
            "ML Anomaly Detection",
            "Rule-Based Threats",
            "Audit Logging"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug,
        "features": {
            "ml_detection": True,
            "rule_based_threats": True,
            "rate_limiting": True,
            "audit_logging": True
        }
    }

@app.get("/api/v1/status")
async def api_status():
    return {
        "service": "Security Gateway",
        "version": "1.0.0",
        "status": "running",
        "protection_layers": 7
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )