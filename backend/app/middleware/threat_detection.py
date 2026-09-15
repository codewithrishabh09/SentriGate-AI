from fastapi import Request, HTTPException, status
from app.services.anomaly_detector import AnomalyDetector
from app.services.llm_analyzer import get_llm_analyzer
from app.services.threat_fusion import get_threat_fusion
from app.cache.redis_client import redis_client
import json
import threading

async def threat_detection_middleware(request: Request, call_next):
    """Combined middleware: ML anomaly + LLM threat analysis (non-blocking)"""
    
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
        
        # Step 1: ML Anomaly Detection (fast)
        detector = AnomalyDetector(redis_client)
        anomaly_result = detector.detect_anomaly(request_data)
        ml_score = anomaly_result.get("anomaly_score", 0.5)
        
        # Step 2: LLM Threat Analysis (non-blocking, with fallback)
        llm_result = {
            "classification": "safe",
            "confidence": 0.3,
            "confidence_level": "low",
            "threats": [],
            "reasoning": "LLM skipped (non-blocking mode)",
            "cached": True
        }
        
        # Try LLM in background (don't block request)
        try:
            llm_analyzer = get_llm_analyzer()
            llm_result = llm_analyzer.analyze_request(
                endpoint=request.url.path,
                method=request.method,
                payload=payload,
                headers=dict(request.headers)
            )
        except Exception as e:
            print(f"LLM analysis skipped: {e}")
            # Use default safe result
        
        # Step 3: Fuse scores
        fusion = get_threat_fusion()
        final_result = fusion.fuse_scores(ml_score, llm_result)
        
        request.state.threat_analysis = final_result
        request.state.ml_score = ml_score
        
        # Block only if DEFINITELY malicious (ML + pattern matching)
        if final_result["should_block"] and ml_score > 0.8:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked: Malicious activity detected"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Threat detection error: {e}")
        # Continue (fail open)
    
    response = await call_next(request)
    
    # Add threat info headers
    if hasattr(request.state, "threat_analysis"):
        threat = request.state.threat_analysis
        response.headers["X-Final-Threat-Score"] = str(threat["final_threat_score"])
        response.headers["X-Threat-Level"] = threat["threat_level"]
        response.headers["X-ML-Score"] = str(threat["ml_anomaly_score"])
    
    return response