from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.config import settings

Base = declarative_base()

# Create engine with proper pool settings for MySQL
engine = create_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()