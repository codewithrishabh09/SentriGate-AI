from sqlalchemy import Column, String, DateTime, func
import uuid
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    role_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Role {self.name}>"