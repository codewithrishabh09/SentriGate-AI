# app/models/api_key.py
class APIKey(Base):
    __tablename__ = "api_keys"
    
    api_key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    key_hash = Column(String(255), unique=True, index=True)
    key_prefix = Column(String(20))  # sk_prod_abc123xx
    status = Column(String(50), default="active")
    rate_limit_requests = Column(Integer, default=1000)
    rate_limit_window_seconds = Column(Integer, default=3600)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)