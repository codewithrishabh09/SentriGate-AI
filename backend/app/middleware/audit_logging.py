from fastapi import Request
from app.services.audit_service import AuditService
import time

async def audit_logging_middleware(request: Request, call_next):
    """Log all requests to audit trail"""
    
    start_time = time.time()
    
    # Extract info
    user_id = None
    ip_address = request.client.host if request.client else "unknown"
    
    try:
        # Try to get user from token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # In a real app, decode the token to get user_id
            pass
    except:
        pass
    
    # Get threat info if available
    threat_level = "safe"
    threat_score = 0.0
    
    response = await call_next(request)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Log to audit trail
    AuditService.log_request(
        user_id=user_id,
        endpoint=request.url.path,
        method=request.method,
        ip_address=ip_address,
        status_code=response.status_code,
        response_time_ms=response_time_ms,
        threat_level=threat_level,
        threat_score=threat_score
    )
    
    return response