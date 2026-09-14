from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

class FeatureExtractor:
    """Extract features from API requests for ML model"""
    
    @staticmethod
    def extract_features(
        request_data: Dict,
        user_history: Dict = None,
        api_key_history: List = None
    ) -> Dict[str, float]:
        """Extract numerical features from request"""
        
        features = {}
        
        # REQUEST-LEVEL FEATURES
        payload = request_data.get("payload", {})
        payload_str = str(payload)
        
        features["payload_size"] = float(len(payload_str.encode()))
        features["payload_size_log"] = float(np.log1p(len(payload_str.encode())))
        features["header_count"] = float(len(request_data.get("headers", {})))
        features["method_is_post"] = float(request_data.get("method") == "POST")
        features["method_is_put"] = float(request_data.get("method") == "PUT")
        features["method_is_patch"] = float(request_data.get("method") == "PATCH")
        features["method_is_delete"] = float(request_data.get("method") == "DELETE")
        
        # USER-LEVEL FEATURES
        if user_history:
            features["requests_per_hour"] = float(user_history.get("requests_per_hour", 0))
            features["requests_per_day"] = float(user_history.get("requests_per_day", 0))
            features["unique_endpoints_count"] = float(user_history.get("unique_endpoints", 0))
            features["days_since_registration"] = float(user_history.get("days_since_registration", 0))
            features["time_since_last_request_hours"] = float(user_history.get("time_since_last_request", 24))
        else:
            features["requests_per_hour"] = 0.0
            features["requests_per_day"] = 0.0
            features["unique_endpoints_count"] = 0.0
            features["days_since_registration"] = 0.0
            features["time_since_last_request_hours"] = 24.0
        
        # API KEY-LEVEL FEATURES
        if api_key_history:
            features["api_key_age_days"] = float(api_key_history.get("age_days", 0))
            features["api_key_requests_count"] = float(api_key_history.get("total_requests", 0))
            features["api_key_requests_today"] = float(api_key_history.get("requests_today", 0))
        else:
            features["api_key_age_days"] = 0.0
            features["api_key_requests_count"] = 0.0
            features["api_key_requests_today"] = 0.0
        
        # TIME-BASED FEATURES
        now = datetime.utcnow()
        features["hour_of_day"] = float(now.hour)
        features["day_of_week"] = float(now.weekday())
        features["is_weekend"] = float(now.weekday() >= 5)
        features["is_business_hours"] = float(9 <= now.hour <= 17)
        
        features["unusual_time_access"] = float(
            (now.hour < 6 or now.hour > 22) and features["is_business_hours"] == 0
        )
        
        return features


def build_feature_vector(features: Dict[str, float]) -> np.ndarray:
    """Convert feature dictionary to ordered numpy array"""
    
    feature_order = [
        "payload_size",
        "payload_size_log",
        "header_count",
        "method_is_post",
        "method_is_put",
        "method_is_patch",
        "method_is_delete",
        "requests_per_hour",
        "requests_per_day",
        "unique_endpoints_count",
        "days_since_registration",
        "time_since_last_request_hours",
        "api_key_age_days",
        "api_key_requests_count",
        "api_key_requests_today",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "is_business_hours",
        "unusual_time_access",
    ]
    
    vector = np.array([features.get(f, 0.0) for f in feature_order])
    return vector.reshape(1, -1)