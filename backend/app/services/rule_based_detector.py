from typing import Dict
import json

class RuleBasedThreatDetector:
    """Ultra-fast rule-based detection"""
    
    def __init__(self):
        # Pre-compiled threat keywords (no regex, pure string matching)
        self.dangerous_keywords = {
            "sql": ["union", "select", "insert", "delete", "drop", "update", "exec(", "execute(", "or 1=1"],
            "cmd": ["bash", "sh ", "cmd", "powershell", "system", "/bin/", "nc -l", "&&", "||", "|"],
            "script": ["<script", "javascript:", "onerror=", "onload=", "eval(", "iframe"],
            "path": ["../", "..\\", "/etc/", "\\windows\\", "/passwd", "/shadow"],
        }
    
    def detect_threats(self, payload: Dict) -> Dict:
        """Instant threat detection (no JSON conversion)"""
        
        if not payload:
            return self._safe_result()
        
        try:
            # Quick size check
            payload_str = str(payload).upper()
            
            if len(payload_str) > 1000000:
                return {
                    "classification": "malicious",
                    "confidence": 0.9,
                    "confidence_level": "high",
                    "threats": ["oversized_payload"],
                    "reasoning": "Payload too large",
                    "risk_score": 0.9,
                    "cached": False
                }
            
            threats_found = []
            risk_score = 0.0
            
            # Fast keyword matching (single pass)
            for category, keywords in self.dangerous_keywords.items():
                for keyword in keywords:
                    if keyword in payload_str:
                        threats_found.append(category)
                        risk_score += 0.25
                        break
            
            risk_score = min(1.0, risk_score)
            
            if risk_score > 0.7:
                classification = "malicious"
            elif risk_score > 0.4:
                classification = "suspicious"
            else:
                classification = "safe"
            
            return {
                "classification": classification,
                "confidence": risk_score,
                "confidence_level": "high",
                "threats": threats_found,
                "reasoning": f"Threats: {len(threats_found)}" if threats_found else "No threats",
                "risk_score": risk_score,
                "cached": False
            }
        
        except:
            return self._safe_result()
    
    def _safe_result(self):
        """Default safe response"""
        return {
            "classification": "safe",
            "confidence": 0.0,
            "confidence_level": "low",
            "threats": [],
            "reasoning": "No threats detected",
            "risk_score": 0.0,
            "cached": False
        }


def get_rule_detector() -> RuleBasedThreatDetector:
    return RuleBasedThreatDetector()