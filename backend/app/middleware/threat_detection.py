from fastapi import Request, HTTPException, status
from app.services.anomaly_detector import AnomalyDetector
from app.services.llm_analyzer import get_llm_analyzer
from app.services.threat_fusion import get_threat_fusion
from app.cache.redis_client import redis_client
import json

async def threat_detection_middleware(request: Request, call_next):
    """Fast threat detection middleware"""
    
    if not request.url.path.startswith("/api/v1"):
        return await call_next(request)
    
    try:
        # Extract payload
        payload = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    payload = json.loads(body)
            except:
                pass
        
        # Quick threat check
        analyzer = get_llm_analyzer()
        threat_result = analyzer.analyze_request(
            endpoint=request.url.path,
            method=request.method,
            payload=payload
        )
        
        # Block immediately if malicious
        if threat_result["classification"] == "malicious":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked: Threat detected"
            )
        
        request.state.threat_result = threat_result
    
    except HTTPException:
        raise
    except:
        pass  # Continue on error
    
    response = await call_next(request)
    
    # Add headers
    if hasattr(request.state, "threat_result"):
        threat = request.state.threat_result
        response.headers["X-Threat-Level"] = threat["classification"]
        response.headers["X-Threat-Score"] = str(threat["confidence"])
    
    return response