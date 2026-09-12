from fastapi import Request
from app.cache.redis_client import redis_client
from app.services.anomaly_detector import AnomalyDetector
from app.database import SessionLocal
from app.models.user import User
from app.models.api_key import APIKey
import json

async def anomaly_detection_middleware(request: Request, call_next):
    """
    Middleware to detect anomalous requests
    """
    
    # Skip for non-API endpoints
    if not request.url.path.startswith("/api/v1"):
        return await call_next(request)
    
    try:
        # Extract request data
        request_data = {
            "method": request.method,
            "endpoint": request.url.path,
            "headers": dict(request.headers),
        }
        
        # Try to get body for POST/PUT
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_data["payload"] = json.loads(body)
            except:
                pass
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        # Get user history if authenticated
        user_history = None
        api_key_history = None
        
        if api_key:
            db = SessionLocal()
            try:
                api_key_obj = db.query(APIKey).filter(
                    APIKey.key_hash == api_key
                ).first()
                
                if api_key_obj:
                    api_key_history = {
                        "age_days": 0,  # Would calculate from created_at
                        "total_requests": 0,  # Would get from DB
                        "requests_today": 0,
                    }
                    
                    user = db.query(User).filter(
                        User.user_id == api_key_obj.user_id
                    ).first()
                    
                    if user:
                        user_history = {
                            "requests_per_hour": 0,
                            "requests_per_day": 0,
                            "unique_endpoints": 0,
                            "days_since_registration": 0,
                            "time_since_last_request": 24,
                        }
            finally:
                db.close()
        
        # Run anomaly detection
        detector = AnomalyDetector(redis_client)
        anomaly_result = detector.detect_anomaly(
            request_data,
            user_history,
            api_key_history
        )
        
        # Add to request state
        request.state.anomaly_score = anomaly_result.get("anomaly_score", 0.5)
        request.state.threat_level = anomaly_result.get("threat_level", "unknown")
        
        # Block if malicious
        if anomaly_result.get("threat_level") == "malicious":
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked due to suspicious activity"
            )
    
    except Exception as e:
        print(f"Error in anomaly detection middleware: {e}")
        # Continue anyway (fail open)
    
    response = await call_next(request)
    
    # Add anomaly info to response headers
    if hasattr(request.state, "anomaly_score"):
        response.headers["X-Anomaly-Score"] = str(request.state.anomaly_score)
        response.headers["X-Threat-Level"] = request.state.threat_level
    
    return response