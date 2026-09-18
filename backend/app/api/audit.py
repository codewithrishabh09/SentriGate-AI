from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLog, ThreatEvent, SecurityAlert
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    endpoint: str = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = db.query(AuditLog).filter(AuditLog.created_at >= cutoff_date)
    
    if endpoint:
        query = query.filter(AuditLog.endpoint.contains(endpoint))
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "logs": [{
            "id": log.id,
            "endpoint": log.endpoint,
            "method": log.method,
            "status_code": log.status_code,
            "threat_level": log.threat_level,
            "threat_score": log.threat_score,
            "response_time_ms": log.response_time_ms,
            "created_at": log.created_at.isoformat()
        } for log in logs]
    }


@router.get("/threats")
async def get_threat_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    classification: str = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get threat events"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = db.query(ThreatEvent).filter(ThreatEvent.created_at >= cutoff_date)
    
    if classification:
        query = query.filter(ThreatEvent.threat_classification == classification)
    
    total = query.count()
    threats = query.order_by(ThreatEvent.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "threats": [{
            "id": threat.id,
            "endpoint": threat.endpoint,
            "classification": threat.threat_classification,
            "score": threat.threat_score,
            "action": threat.action_taken,
            "detection_method": threat.detection_method,
            "created_at": threat.created_at.isoformat()
        } for threat in threats]
    }


@router.get("/alerts")
async def get_security_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    severity: str = Query(None),
    resolved: bool = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get security alerts"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = db.query(SecurityAlert).filter(SecurityAlert.created_at >= cutoff_date)
    
    if severity:
        query = query.filter(SecurityAlert.severity == severity)
    
    if resolved is not None:
        query = query.filter(SecurityAlert.is_resolved == resolved)
    
    total = query.count()
    alerts = query.order_by(SecurityAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "alerts": [{
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "is_resolved": alert.is_resolved,
            "created_at": alert.created_at.isoformat()
        } for alert in alerts]
    }


@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get security dashboard stats"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_requests = db.query(AuditLog).filter(AuditLog.created_at >= today).count()
    threats_detected = db.query(ThreatEvent).filter(ThreatEvent.created_at >= today).count()
    malicious_blocked = db.query(ThreatEvent).filter(
        ThreatEvent.threat_classification == "malicious",
        ThreatEvent.created_at >= today
    ).count()
    critical_alerts = db.query(SecurityAlert).filter(
        SecurityAlert.severity == "critical",
        SecurityAlert.created_at >= today,
        SecurityAlert.is_resolved == False
    ).count()
    
    return {
        "date": today.isoformat(),
        "stats": {
            "total_requests": total_requests,
            "threats_detected": threats_detected,
            "malicious_blocked": malicious_blocked,
            "critical_alerts": critical_alerts
        }
    }