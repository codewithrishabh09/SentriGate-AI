# app/cache/llm_cache.py
async def get_llm_analysis(request_hash: str, redis_client):
    """Check cache before calling expensive LLM API"""
    cache_key = f"llm_cache:{request_hash}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Call LLM
    result = await analyze_threat(request)
    redis_client.setex(cache_key, 86400, json.dumps(result))  # Cache 24h
    return result