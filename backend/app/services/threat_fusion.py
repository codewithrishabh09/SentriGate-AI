from typing import Dict, Tuple

class ThreatFusion:
    """Combine ML and LLM scores for final threat decision"""
    
    @staticmethod
    def fuse_scores(
        ml_anomaly_score: float,
        llm_threat_info: Dict
    ) -> Dict:
        """
        Fuse ML anomaly score with LLM threat analysis
        
        Weighting:
        - 40% ML anomaly score (detects unusual patterns)
        - 60% LLM threat score (detects intent & injection)
        
        Returns:
            {
                "final_threat_score": 0.0-1.0,
                "threat_level": "safe" | "suspicious" | "malicious",
                "should_block": True/False,
                "ml_contribution": ...,
                "llm_contribution": ...,
                "reasoning": "..."
            }
        """
        
        # Get LLM score
        llm_score = llm_threat_info.get("confidence", 0.5)
        
        # Weighted fusion
        weights = {
            "ml": 0.4,      # 40% ML anomaly
            "llm": 0.6      # 60% LLM threat
        }
        
        final_score = (
            ml_anomaly_score * weights["ml"] +
            llm_score * weights["llm"]
        )
        
        # Determine threat level
        if final_score > 0.85:
            threat_level = "malicious"
            should_block = True
        elif final_score > 0.65:
            threat_level = "suspicious"
            should_block = False  # Log, don't block yet
        else:
            threat_level = "safe"
            should_block = False
        
        # Build reasoning
        reasoning = ThreatFusion._build_reasoning(
            ml_anomaly_score,
            llm_threat_info,
            final_score,
            threat_level
        )
        
        return {
            "final_threat_score": float(final_score),
            "threat_level": threat_level,
            "should_block": should_block,
            "ml_anomaly_score": float(ml_anomaly_score),
            "llm_threat_score": float(llm_score),
            "ml_contribution": float(ml_anomaly_score * weights["ml"]),
            "llm_contribution": float(llm_score * weights["llm"]),
            "llm_classification": llm_threat_info.get("classification", "unknown"),
            "llm_confidence": llm_threat_info.get("confidence_level", "low"),
            "threats_detected": llm_threat_info.get("threats", []),
            "reasoning": reasoning
        }
    
    @staticmethod
    def _build_reasoning(
        ml_score: float,
        llm_info: Dict,
        final_score: float,
        threat_level: str
    ) -> str:
        """Build human-readable reasoning"""
        
        parts = []
        
        # ML component
        if ml_score > 0.7:
            parts.append(f"ML: Anomalous pattern detected ({ml_score:.2f})")
        else:
            parts.append(f"ML: Normal pattern ({ml_score:.2f})")
        
        # LLM component
        llm_class = llm_info.get("classification", "unknown").upper()
        llm_reason = llm_info.get("reasoning", "")
        parts.append(f"LLM: {llm_class} - {llm_reason[:100]}")
        
        # Final decision
        if threat_level == "malicious":
            parts.append("DECISION: Block request")
        elif threat_level == "suspicious":
            parts.append("DECISION: Log and monitor")
        else:
            parts.append("DECISION: Allow request")
        
        return " | ".join(parts)


def get_threat_fusion() -> ThreatFusion:
    """Get threat fusion instance"""
    return ThreatFusion()