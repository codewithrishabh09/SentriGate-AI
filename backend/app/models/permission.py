from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Permission(Base):
    __tablename__ = "permissions"
    
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, index=True, nullable=False)  # view_audit_logs
    description = Column(String(500), nullable=True)
    resource = Column(String(100), nullable=False)  # users, api_keys, threats
    action = Column(String(50), nullable=False)  # read, write, delete, execute
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Permission {self.name}>"