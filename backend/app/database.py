from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.config import settings

# Create Base FIRST - no model imports!
Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL if settings.DATABASE_URL else "sqlite:///./test.db",
    echo=settings.SQLALCHEMY_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in (settings.DATABASE_URL or "sqlite") else {}
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()