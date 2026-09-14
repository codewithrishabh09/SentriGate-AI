from fastapi import Request, HTTPException, status
from app.services.anomaly_detector import AnomalyDetector
from app.services.llm_analyzer import get_llm_analyzer
from app.services.threat_fusion import get_threat_fusion
from app.cache.redis_client import redis_client
from app.database import SessionLocal
from app.models.user import User
from app.models.api_key import APIKey
import json

async def threat_detection_middleware(request: Request, call_next):
    """
    Combined middleware: ML anomaly + LLM threat analysis
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
        
        payload = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_data["payload"] = json.loads(body)
                    payload = request_data["payload"]
            except:
                pass
        
        # Step 1: ML Anomaly Detection
        detector = AnomalyDetector(redis_client)
        anomaly_result = detector.detect_anomaly(request_data)
        ml_score = anomaly_result.get("anomaly_score", 0.5)
        
        # Step 2: LLM Threat Analysis
        llm_analyzer = get_llm_analyzer()
        llm_result = await llm_analyzer.analyze_request(
            endpoint=request.url.path,
            method=request.method,
            payload=payload,
            headers=dict(request.headers)
        )
        
        # Step 3: Fuse scores
        fusion = get_threat_fusion()
        final_result = fusion.fuse_scores(ml_score, llm_result)
        
        # Store in request state
        request.state.threat_analysis = final_result
        request.state.ml_score = ml_score
        request.state.llm_result = llm_result
        
        # Step 4: Make decision
        if final_result["should_block"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked: Malicious activity detected",
                headers={"X-Threat-Level": "malicious"}
            )
        
        # Log suspicious activity
        if final_result["threat_level"] == "suspicious":
            log_suspicious_activity(request, final_result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in threat detection: {e}")
        # Continue anyway (fail open)
    
    response = await call_next(request)
    
    # Add threat info to response headers
    if hasattr(request.state, "threat_analysis"):
        threat = request.state.threat_analysis
        response.headers["X-Final-Threat-Score"] = str(threat["final_threat_score"])
        response.headers["X-Threat-Level"] = threat["threat_level"]
        response.headers["X-ML-Score"] = str(threat["ml_anomaly_score"])
        response.headers["X-LLM-Score"] = str(threat["llm_threat_score"])
    
    return response


def log_suspicious_activity(request: Request, threat_result: Dict):
    """Log suspicious activity for review"""
    
    try:
        db = SessionLocal()
        api_key = request.headers.get("X-API-Key")
        
        log_entry = {
            "timestamp": str(request.state.__dict__.get("timestamp", "")),
            "endpoint": request.url.path,
            "method": request.method,
            "threat_level": threat_result.get("threat_level"),
            "threat_score": threat_result.get("final_threat_score"),
            "ml_score": threat_result.get("ml_anomaly_score"),
            "llm_score": threat_result.get("llm_threat_score"),
            "threats": threat_result.get("threats_detected", []),
            "reasoning": threat_result.get("reasoning", "")
        }
        
        # Log to Redis for monitoring
        if redis_client:
            key = f"suspicious_activity:{api_key}:{request.url.path}"
            redis_client.lpush(key, json.dumps(log_entry))
            redis_client.expire(key, 86400)  # Keep 24 hours
        
        print(f"Suspicious activity logged: {log_entry}")
    
    except Exception as e:
        print(f"Error logging suspicious activity: {e}")
    finally:
        db.close()