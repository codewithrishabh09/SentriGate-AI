import html
import re
from typing import Any, Dict

def sanitize_string(value: str, max_length: int = 10000) -> str:
    """
    Sanitize a string to prevent XSS and injection attacks
    """
    if not isinstance(value, str):
        return str(value)
    
    # Escape HTML special characters
    escaped = html.escape(value)
    
    # Remove common script tags and dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers like onclick=
        r'eval\(',
    ]
    
    for pattern in dangerous_patterns:
        escaped = re.sub(pattern, '', escaped, flags=re.IGNORECASE | re.DOTALL)
    
    # Truncate to max length
    return escaped[:max_length]


def sanitize_dict(data: Dict[str, Any], max_length: int = 10000) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value, max_length)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_length)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item, max_length) if isinstance(item, str)
                else sanitize_dict(item, max_length) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username (alphanumeric, underscore, hyphen only)"""
    pattern = r'^[a-zA-Z0-9_-]{3,100}$'
    return re.match(pattern, username) is not None