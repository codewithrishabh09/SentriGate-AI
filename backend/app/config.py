import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    APP_NAME = "SentriGate AI - API Security Gateway"
    DEBUG = os.getenv("DEBUG", "True") == "True"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/security_gateway"
    )
    SQLALCHEMY_ECHO = DEBUG
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT/Auth
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

settings = Settings()