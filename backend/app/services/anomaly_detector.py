from typing import Dict, Tuple
import json
from app.ml.feature_extractor import FeatureExtractor, build_feature_vector
from app.ml.model_loader import get_ml_manager
import redis
import hashlib

class AnomalyDetector:
    """Detect anomalies in API requests"""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.ml_manager = get_ml_manager()
        self.feature_extractor = FeatureExtractor()
        self.redis_client = redis_client
    
    def detect_anomaly(
        self,
        request_data: Dict,
        user_history: Dict = None,
        api_key_history: Dict = None
    ) -> Dict:
        """
        Detect if request is anomalous
        
        Returns:
            {
                "anomaly_score": 0.0-1.0,
                "is_anomaly": True/False,
                "threat_level": "normal" | "suspicious" | "malicious",
                "features": {...},
                "ml_prediction": 1 or -1
            }
        """
        
        try:
            # Extract features
            features = self.feature_extractor.extract_features(
                request_data,
                user_history,
                api_key_history
            )
            
            # Check cache first
            feature_hash = self._hash_features(features)
            if self.redis_client:
                cached = self.redis_client.get(f"anomaly_score:{feature_hash}")
                if cached:
                    return json.loads(cached)
            
            # Build feature vector
            feature_vector = build_feature_vector(features)
            
            # Score with ML model
            anomaly_score, ml_prediction = self.ml_manager.score_request(feature_vector)
            
            # Determine threat level
            if anomaly_score > 0.9:
                threat_level = "malicious"
            elif anomaly_score > 0.7:
                threat_level = "suspicious"
            else:
                threat_level = "normal"
            
            result = {
                "anomaly_score": float(anomaly_score),
                "is_anomaly": anomaly_score > 0.7,
                "threat_level": threat_level,
                "ml_prediction": ml_prediction,
                "features_used": len(features),
                "features_sample": {
                    "payload_size": features.get("payload_size", 0),
                    "requests_per_hour": features.get("requests_per_hour", 0),
                    "hour_of_day": features.get("hour_of_day", 0),
                }
            }
            
            # Cache result
            if self.redis_client:
                self.redis_client.setex(
                    f"anomaly_score:{feature_hash}",
                    3600,  # Cache for 1 hour
                    json.dumps(result)
                )
            
            return result
        
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return {
                "anomaly_score": 0.5,
                "is_anomaly": False,
                "threat_level": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    def _hash_features(features: Dict) -> str:
        """Create hash of features for caching"""
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.sha256(feature_str.encode()).hexdigest()[:16]