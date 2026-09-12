# app/utils/sanitizer.py
import bleach
import html

def sanitize_string(value: str, max_length: int = 1000) -> str:
    # Remove HTML tags
    cleaned = bleach.clean(value, tags=[], strip=True)
    # Escape special chars
    escaped = html.escape(cleaned)
    # Truncate
    return escaped[:max_length]

def validate_json_payload(data: dict) -> dict:
    """Recursively sanitize JSON"""
    if isinstance(data, dict):
        return {k: validate_json_payload(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [validate_json_payload(item) for item in data]
    elif isinstance(data, str):
        return sanitize_string(data)
    return data