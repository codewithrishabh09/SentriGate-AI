from sqlalchemy import Column, ForeignKey, DateTime, func, String
import uuid
from app.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.role_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    role_perm_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(String(36), ForeignKey("roles.role_id"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.permission_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())