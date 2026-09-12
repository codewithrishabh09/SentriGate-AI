# app/ml/features.py
import numpy as np
from datetime import datetime

def extract_features(request: dict, user_history: dict) -> dict:
    """Extract features for ML model"""
    features = {
        # Request-level features
        "payload_size": len(str(request.get("payload", {}))),
        "header_count": len(request.get("headers", {})),
        "method_is_post": int(request.get("method") == "POST"),
        
        # User-level features
        "requests_per_hour": user_history.get("req_per_hour", 0),
        "unique_endpoints_per_day": user_history.get("unique_endpoints", 0),
        "time_since_last_request": compute_time_diff(user_history.get("last_request")),
        
        # Behavioral features
        "hour_of_day": datetime.utcnow().hour,
        "day_of_week": datetime.utcnow().weekday(),
        "is_unusual_time": is_unusual_time(user_history),
    }
    return features