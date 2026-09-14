from fastapi import Request, HTTPException, status
from app.services.anomaly_detector import AnomalyDetector
from app.services.llm_analyzer import get_llm_analyzer
from app.services.threat_fusion import get_threat_fusion
from app.cache.redis_client import redis_client
from app.database import SessionLocal
import json

async def threat_detection_middleware(request: Request, call_next):
    """Combined middleware: ML anomaly + LLM threat analysis"""
    
    if not request.url.path.startswith("/api/v1"):
        return await call_next(request)
    
    try:
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
        
        # ML Anomaly Detection
        detector = AnomalyDetector(redis_client)
        anomaly_result = detector.detect_anomaly(request_data)
        ml_score = anomaly_result.get("anomaly_score", 0.5)
        
        # LLM Threat Analysis (skip if no OpenAI key)
        from app.config import settings
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "REDACTED_OPENAI_KEY":
            llm_analyzer = get_llm_analyzer()
            llm_result = await llm_analyzer.analyze_request(
                endpoint=request.url.path,
                method=request.method,
                payload=payload,
                headers=dict(request.headers)
            )
        else:
            # Fallback if no LLM
            llm_result = {
                "classification": "safe",
                "confidence": 0.5,
                "confidence_level": "low",
                "threats": [],
                "reasoning": "LLM not configured",
                "cached": True
            }
        
        # Fuse scores
        fusion = get_threat_fusion()
        final_result = fusion.fuse_scores(ml_score, llm_result)
        
        request.state.threat_analysis = final_result
        request.state.ml_score = ml_score
        request.state.llm_result = llm_result
        
        # Block if malicious
        if final_result["should_block"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked: Malicious activity detected",
                headers={"X-Threat-Level": "malicious"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Threat detection error: {e}")
    
    response = await call_next(request)
    
    if hasattr(request.state, "threat_analysis"):
        threat = request.state.threat_analysis
        response.headers["X-Final-Threat-Score"] = str(threat["final_threat_score"])
        response.headers["X-Threat-Level"] = threat["threat_level"]
        response.headers["X-ML-Score"] = str(threat["ml_anomaly_score"])
        response.headers["X-LLM-Score"] = str(threat["llm_threat_score"])
    
    return response