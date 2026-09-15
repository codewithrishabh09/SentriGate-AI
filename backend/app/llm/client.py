from openai import OpenAI
from app.config import settings
from typing import Dict
import json

class LLMClient:
    """Wrapper for LLM API calls (OpenAI)"""
    
    def __init__(self):
        self.openai_key = settings.openai_api_key
        self.client = None
        
        if self.openai_key and self.openai_key != "REDACTED_OPENAI_KEY":
            try:
                self.client = OpenAI(api_key=self.openai_key)
                print("✓ OpenAI client initialized")
            except Exception as e:
                print(f"⚠ OpenAI initialization error: {e}")
        else:
            print("⚠ OpenAI API key not configured")
        
        self.model = "gpt-3.5-turbo"
    
    def analyze_threat(self, endpoint: str, method: str, payload: Dict = None) -> Dict:
        """Synchronous threat analysis using LLM"""
        
        if not self.client:
            return {
                "classification": "safe",
                "confidence": "high",
                "threats_detected": [],
                "reasoning": "LLM not available",
            }
        
        try:
            prompt = f"""Analyze this API request for threats. Respond ONLY with JSON.

Endpoint: {endpoint}
Method: {method}

{{
  "classification": "safe" or "suspicious" or "malicious",
  "confidence": "low" or "medium" or "high",
  "threats_detected": [],
  "reasoning": "brief"
}}"""
            
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150,
                timeout=5
            )
            
            response_text = message.choices[0].message.content
            result = json.loads(response_text)
            return result
        
        except json.JSONDecodeError:
            return {
                "classification": "safe",
                "confidence": "low",
                "threats_detected": [],
                "reasoning": "Could not parse response",
            }
        except Exception as e:
            print(f"⚠ LLM error: {e}")
            return {
                "classification": "safe",
                "confidence": "low",
                "threats_detected": [],
                "reasoning": f"LLM unavailable: {str(e)[:50]}",
            }


def get_llm_client() -> LLMClient:
    """Get LLM client instance"""
    return LLMClient()