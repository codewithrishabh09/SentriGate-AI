from typing import Dict
from app.services.rule_based_detector import get_rule_detector

class LLMThreatAnalyzer:
    """Threat analyzer using rules (fast, no API)"""
    
    def __init__(self):
        self.detector = get_rule_detector()
    
    def analyze_request(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> Dict:
        """Fast rule-based analysis"""
        
        result = self.detector.detect_threats(payload or {})
        
        return {
            "classification": result["classification"],
            "confidence": result["risk_score"],
            "confidence_level": "high",
            "threats": result["threats"],
            "reasoning": result["reasoning"],
            "cached": False
        }


def get_llm_analyzer():
    """Get analyzer instance"""
    return LLMThreatAnalyzer()