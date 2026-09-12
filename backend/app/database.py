from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    future=True
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=Session
)

# Base class for all models
Base = declarative_base()

# Dependency for FastAPI
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()