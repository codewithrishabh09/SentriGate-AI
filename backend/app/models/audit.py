from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    request_size = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    threat_level = Column(String(50), nullable=True)
    threat_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.endpoint} {self.status_code}>"


class ThreatEvent(Base):
    __tablename__ = "threat_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    api_key_id = Column(String(36), nullable=True)
    endpoint = Column(String(255), nullable=False)
    threat_classification = Column(String(50), nullable=False)  # safe, suspicious, malicious
    threat_score = Column(Float, nullable=False)
    threat_details = Column(Text, nullable=True)
    detection_method = Column(String(100), nullable=False)  # ml, rules, rate_limit
    action_taken = Column(String(50), nullable=False)  # allowed, blocked, reviewed
    ip_address = Column(String(45), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ThreatEvent {self.threat_classification} {self.threat_score}>"


class SecurityAlert(Base):
    __tablename__ = "security_alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    alert_type = Column(String(100), nullable=False)  # failed_login, brute_force, dos, etc
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<SecurityAlert {self.alert_type} {self.severity}>"