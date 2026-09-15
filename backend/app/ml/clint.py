from openai import OpenAI
from app.config import settings
from typing import Dict
import json
import time

class LLMClient:
    """Wrapper for LLM API calls (OpenAI)"""
    
    def __init__(self):
        self.openai_key = settings.openai_api_key
        if self.openai_key and self.openai_key != "REDACTED_OPENAI_KEY":
            self.client = OpenAI(api_key=self.openai_key)
        else:
            self.client = None
        self.model = "gpt-3.5-turbo"
        self.timeout = 10
    
    async def analyze_threat(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> Dict:
        """Use LLM to analyze API request for threats"""
        
        if not self.client:
            return {
                "classification": "safe",
                "confidence": "high",
                "threats_detected": [],
                "reasoning": "LLM not configured",
                "recommendations": ""
            }
        
        try:
            prompt = self._build_analysis_prompt(endpoint, method, payload, headers)
            
            start_time = time.time()
            response = self._call_openai(prompt)
            elapsed = time.time() - start_time
            
            result = self._parse_threat_response(response)
            result["response_time_ms"] = int(elapsed * 1000)
            
            return result
        
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return {
                "classification": "suspicious",
                "confidence": "low",
                "threats_detected": [],
                "reasoning": f"LLM analysis failed: {str(e)}",
                "recommendations": "Manual review required",
                "error": str(e)
            }
    
    def _build_analysis_prompt(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> str:
        """Build prompt for threat analysis"""
        
        payload_str = json.dumps(payload, indent=2)[:500] if payload else "{}"
        headers_str = json.dumps({k: v for k, v in headers.items() if k.lower() not in ['authorization']}, indent=2)[:200] if headers else "{}"
        
        prompt = f"""Analyze this API request for security threats.

ENDPOINT: {endpoint}
METHOD: {method}
PAYLOAD: {payload_str}

Respond ONLY with JSON:
{{
  "classification": "safe" or "suspicious" or "malicious",
  "confidence": "low" or "medium" or "high",
  "threats_detected": [],
  "reasoning": "brief",
  "recommendations": "brief"
}}"""
        
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API using new 1.0.0+ syntax"""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security analyst. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                timeout=self.timeout
            )
            
            return message.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")
    
    @staticmethod
    def _parse_threat_response(response_text: str) -> Dict:
        """Parse LLM response"""
        
        try:
            result = json.loads(response_text)
            
            required = ["classification", "confidence", "threats_detected", "reasoning"]
            for field in required:
                if field not in result:
                    result[field] = None
            
            return result
        
        except json.JSONDecodeError:
            return {
                "classification": "safe",
                "confidence": "low",
                "threats_detected": [],
                "reasoning": "Could not parse LLM response",
                "recommendations": "Review manually"
            }
    
    async def detect_injection_attempt(self, payload: Dict) -> bool:
        """Quick check for obvious injection patterns"""
        
        dangerous_keywords = [
            "DROP TABLE", "DELETE FROM", "INSERT INTO",
            "SELECT", "UNION", "OR 1=1",
            "bash", "sh", "cmd", "powershell",
            "eval", "exec", "system",
            "/bin/sh", "nc -l", "cat /etc/passwd"
        ]
        
        payload_str = json.dumps(payload).upper()
        
        for keyword in dangerous_keywords:
            if keyword in payload_str:
                return True
        
        return False


def get_llm_client() -> LLMClient:
    """Get LLM client instance"""
    return LLMClient()