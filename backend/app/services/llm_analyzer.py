from typing import Dict, Tuple
import json
from app.llm.client import get_llm_client
from app.cache.redis_client import redis_client
import hashlib

class LLMThreatAnalyzer:
    """Analyze threats using LLM"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def analyze_request(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> Dict:
        """
        Analyze request using LLM
        
        Returns:
            {
                "classification": "safe" | "suspicious" | "malicious",
                "confidence": 0.0-1.0,
                "threats": [...],
                "reasoning": "...",
                "cached": True/False
            }
        """
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(endpoint, method, payload)
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    result = json.loads(cached)
                    result["cached"] = True
                    return result
            
            # Quick injection check first
            has_injection = await self.llm_client.detect_injection_attempt(payload or {})
            
            if has_injection:
                result = {
                    "classification": "malicious",
                    "confidence": 0.95,
                    "confidence_level": "high",
                    "threats": ["Injection attempt detected"],
                    "reasoning": "Dangerous keywords detected in payload",
                    "cached": False,
                    "quick_check": True
                }
            else:
                # Full LLM analysis
                llm_response = await self.llm_client.analyze_threat(
                    endpoint, method, payload, headers
                )
                
                result = {
                    "classification": llm_response.get("classification", "suspicious"),
                    "confidence": self._confidence_to_score(
                        llm_response.get("confidence", "low")
                    ),
                    "confidence_level": llm_response.get("confidence", "low"),
                    "threats": llm_response.get("threats_detected", []),
                    "reasoning": llm_response.get("reasoning", ""),
                    "recommendations": llm_response.get("recommendations", ""),
                    "cached": False,
                    "response_time_ms": llm_response.get("response_time_ms", 0)
                }
            
            # Cache result
            if redis_client:
                redis_client.setex(
                    cache_key,
                    3600,  # Cache for 1 hour
                    json.dumps(result)
                )
            
            return result
        
        except Exception as e:
            print(f"LLM analyzer error: {e}")
            return {
                "classification": "suspicious",
                "confidence": 0.5,
                "confidence_level": "low",
                "threats": [],
                "reasoning": f"Analysis failed: {str(e)}",
                "cached": False,
                "error": str(e)
            }
    
    @staticmethod
    def _confidence_to_score(confidence: str) -> float:
        """Convert confidence level to score"""
        mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9
        }
        return mapping.get(confidence.lower(), 0.5)
    
    @staticmethod
    def _get_cache_key(endpoint: str, method: str, payload: Dict) -> str:
        """Generate cache key for LLM analysis"""
        key_data = f"{endpoint}:{method}:{json.dumps(payload, sort_keys=True)}"
        hash_val = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"llm_threat:{hash_val}"


def get_llm_analyzer() -> LLMThreatAnalyzer:
    """Get LLM analyzer instance"""
    return LLMThreatAnalyzer()