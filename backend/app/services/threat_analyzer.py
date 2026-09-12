# app/services/threat_analyzer.py
async def classify_request(request: dict, ml_score: float, redis_client):
    """Combine ML + LLM for final classification"""
    
    # LLM analysis
    llm_result = await analyze_threat(request)
    
    # Combine scores
    final_score = (ml_score * 0.4) + (llm_result['confidence'] * 0.6)
    
    # Decision logic
    if final_score > 0.8 and llm_result['classification'] == 'malicious':
        return {"action": "block", "reason": llm_result['reasoning']}
    elif final_score > 0.6:
        return {"action": "review", "reason": "High risk detected"}
    else:
        return {"action": "allow", "reason": "Normal request"}