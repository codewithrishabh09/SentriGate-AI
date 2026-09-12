# app/services/audit.py
async def log_audit_event(
    db: Session,
    user_id: str,
    action_type: str,
    resource_type: str,
    result: dict,
    ip_address: str
):
    audit_log = AuditLog(
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        result=result,
        ip_address=ip_address,
        created_at=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    # Also log to external system
    logger.info({
        "action": action_type,
        "user_id": user_id,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })