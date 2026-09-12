# app/llm/client.py
import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

async def analyze_threat(request: dict) -> dict:
    """Use LLM to analyze potential threat"""
    
    prompt = f"""
    Analyze this API request for security threats.
    
    Endpoint: {request['endpoint']}
    Method: {request['method']}
    Payload: {str(request['payload'])[:500]}  # Truncate for brevity
    
    Check for:
    1. Prompt injection attempts
    2. Data exfiltration patterns
    3. Unusual request patterns
    4. Malicious intent
    
    Respond with JSON: {{"classification": "safe|suspicious|malicious", "confidence": 0.0-1.0, "reasoning": "..."}}
    """
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    
    return json.loads(response['choices'][0]['message']['content'])