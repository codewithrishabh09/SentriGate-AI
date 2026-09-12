# app/ml/scorer.py
from app.ml.model_loader import load_or_train_model
from app.cache.redis_client import redis_client

async def score_request(features: dict, api_key: str):
    """Get anomaly score (0=normal, 1=anomalous)"""
    
    # Check cache first
    cache_key = f"ml_score:{hash(str(features))}"
    cached = redis_client.get(cache_key)
    if cached:
        return float(cached)
    
    # Load model
    model = load_or_train_model()
    
    # Prepare features
    feature_array = np.array([list(features.values())])
    
    # Get anomaly score
    score = model.decision_function(feature_array)[0]
    normalized_score = 1 / (1 + np.exp(-score))  # Sigmoid to [0, 1]
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, normalized_score)
    
    return normalized_score