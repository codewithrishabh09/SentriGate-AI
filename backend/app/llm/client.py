import openai
from app.config import settings
from typing import Dict, Optional, Tuple
import json
import time

class LLMClient:
    """Wrapper for LLM API calls (OpenAI/Claude)"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        if self.openai_key and self.openai_key != "sk-xxxxx":
            openai.api_key = self.openai_key
        self.model = "gpt-3.5-turbo"  # Fast & cheap
        self.timeout = 3  # 3 second timeout
    
    async def analyze_threat(
        self,
        endpoint: str,
        method: str,
        payload: Dict = None,
        headers: Dict = None
    ) -> Dict:
        """
        Use LLM to analyze API request for threats
        
        Returns:
            {
                "classification": "safe" | "suspicious" | "malicious",
                "confidence": "low" | "medium" | "high",
                "threats_detected": [...],
                "reasoning": "...",
                "recommendations": "..."
            }
        """
        
        if not self.openai_key or self.openai_key == "sk-xxxxx":
            # No API key, return safe
            return {
                "classification": "safe",
                "confidence": "high",
                "threats_detected": [],
                "reasoning": "LLM not configured",
                "recommendations": ""
            }
        
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(endpoint, method, payload, headers)
            
            # Call LLM
            start_time = time.time()
            response = await self._call_openai(prompt)
            elapsed = time.time() - start_time
            
            # Parse response
            result = self._parse_threat_response(response)
            result["response_time_ms"] = int(elapsed * 1000)
            
            return result
        
        except Exception as e:
            print(f"LLM error: {e}")
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
        headers_str = json.dumps(headers, indent=2)[:200] if headers else "{}"
        
        prompt = f"""You are a security analyst. Analyze this API request for threats.

ENDPOINT: {endpoint}
METHOD: {method}
PAYLOAD (truncated): {payload_str}
HEADERS (truncated): {headers_str}

Analyze for:
1. Prompt injection attempts (SQL, shell commands, jailbreaks)
2. Data exfiltration patterns
3. Unauthorized access attempts
4. Malicious payload patterns
5. Suspicious behavior

Respond ONLY with valid JSON (no markdown, no explanations):
{{
  "classification": "safe" or "suspicious" or "malicious",
  "confidence": "low" or "medium" or "high",
  "threats_detected": ["threat1", "threat2"],
  "reasoning": "brief explanation",
  "recommendations": "brief recommendation"
}}

Be concise. Respond immediately."""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with timeout"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature = consistent, logical
                max_tokens=200,
                timeout=self.timeout
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    @staticmethod
    def _parse_threat_response(response_text: str) -> Dict:
        """Parse LLM response"""
        
        try:
            # Try to parse JSON
            result = json.loads(response_text)
            
            # Validate required fields
            required = ["classification", "confidence", "threats_detected", "reasoning"]
            for field in required:
                if field not in result:
                    result[field] = None
            
            return result
        
        except json.JSONDecodeError:
            # If JSON parsing fails, extract key info
            return {
                "classification": "suspicious",
                "confidence": "low",
                "threats_detected": [],
                "reasoning": response_text[:200],
                "recommendations": "Manual review recommended"
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