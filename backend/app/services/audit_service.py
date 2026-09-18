from app.models.audit import AuditLog, ThreatEvent, SecurityAlert
from app.database import SessionLocal
from datetime import datetime
import time

class AuditService:
    """Service for logging and tracking security events"""
    
    @staticmethod
    def log_request(
        user_id: str = None,
        endpoint: str = None,
        method: str = None,
        ip_address: str = None,
        status_code: int = None,
        response_time_ms: int = None,
        threat_level: str = None,
        threat_score: float = None
    ):
        """Log API request"""
        try:
            db = SessionLocal()
            log = AuditLog(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                status_code=status_code,
                response_time_ms=response_time_ms,
                threat_level=threat_level,
                threat_score=threat_score
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Error logging request: {e}")
    
    @staticmethod
    def log_threat(
        user_id: str = None,
        endpoint: str = None,
        threat_classification: str = None,
        threat_score: float = None,
        threat_details: str = None,
        detection_method: str = None,
        action_taken: str = None,
        ip_address: str = None
    ):
        """Log threat event"""
        try:
            db = SessionLocal()
            event = ThreatEvent(
                user_id=user_id,
                endpoint=endpoint,
                threat_classification=threat_classification,
                threat_score=threat_score,
                threat_details=threat_details,
                detection_method=detection_method,
                action_taken=action_taken,
                ip_address=ip_address
            )
            db.add(event)
            db.commit()
            
            # Create alert if malicious
            if threat_classification == "malicious":
                AuditService.create_alert(
                    alert_type="malicious_request",
                    severity="critical",
                    title=f"Malicious request blocked: {endpoint}",
                    description=f"Threat score: {threat_score}, IP: {ip_address}",
                    ip_address=ip_address,
                    user_id=user_id,
                    db=db
                )
            
            db.close()
        except Exception as e:
            print(f"Error logging threat: {e}")
    
    @staticmethod
    def create_alert(
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        ip_address: str = None,
        user_id: str = None,
        db=None
    ):
        """Create security alert"""
        try:
            should_close = False
            if not db:
                db = SessionLocal()
                should_close = True
            
            alert = SecurityAlert(
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                ip_address=ip_address
            )
            db.add(alert)
            db.commit()
            
            if should_close:
                db.close()
        except Exception as e:
            print(f"Error creating alert: {e}")


def get_audit_service() -> AuditService:
    return AuditService()