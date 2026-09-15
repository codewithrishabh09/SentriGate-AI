from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    app_name: str = "SentriGate AI"
    environment: str = "development"
    debug: bool = True
    
    database_url: str = "sqlite:///./test.db"
    sqlalchemy_echo: bool = False
    
    redis_url: str = "redis://localhost:6379/0"
    
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    allowed_origins: List[str] = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()

# Backwards compatibility
settings.APP_NAME = settings.app_name
settings.ENVIRONMENT = settings.environment
settings.DEBUG = settings.debug
settings.DATABASE_URL = settings.database_url
settings.SQLALCHEMY_ECHO = settings.sqlalchemy_echo
settings.REDIS_URL = settings.redis_url
settings.SECRET_KEY = settings.secret_key
settings.ALGORITHM = settings.algorithm
settings.ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
settings.ALLOWED_ORIGINS = settings.allowed_origins
settings.LOG_LEVEL = settings.log_level