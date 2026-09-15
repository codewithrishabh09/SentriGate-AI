from typing import Dict
from app.llm.client import get_llm_client

class LLMThreatAnalyzer:
    """Analyze threats using LLM (non-blocking)"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze_request(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> Dict:
        """Analyze request using LLM (synchronous)"""
        
        try:
            result = self.llm_client.analyze_threat(endpoint, method, payload)
            
            return {
                "classification": result.get("classification", "safe"),
                "confidence": self._confidence_to_score(result.get("confidence", "low")),
                "confidence_level": result.get("confidence", "low"),
                "threats": result.get("threats_detected", []),
                "reasoning": result.get("reasoning", ""),
                "cached": False
            }
        
        except Exception as e:
            print(f"LLM analyzer error: {e}")
            return {
                "classification": "safe",
                "confidence": 0.3,
                "confidence_level": "low",
                "threats": [],
                "reasoning": "LLM analysis skipped",
                "cached": False
            }
    
    @staticmethod
    def _confidence_to_score(confidence: str) -> float:
        """Convert confidence level to score"""
        mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9
        }
        return mapping.get(str(confidence).lower(), 0.5)


def get_llm_analyzer() -> LLMThreatAnalyzer:
    """Get LLM analyzer instance"""
    return LLMThreatAnalyzer()