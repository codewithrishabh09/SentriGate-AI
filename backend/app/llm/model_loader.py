import joblib
import numpy as np
import os
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional

class MLModelManager:
    """Manage ML models for anomaly detection"""
    
    def __init__(self, model_dir: str = "/tmp/ml_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model = None
        self.scaler = None
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_path = f"{self.model_dir}/isolation_forest_v1.pkl"
        scaler_path = f"{self.model_dir}/scaler_v1.pkl"
        
        if os.path.exists(model_path):
            print("Loading existing model...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        else:
            print("Creating new model...")
            self._create_default_model()
    
    def _create_default_model(self):
        """Create and train default model with synthetic data"""
        
        # Create synthetic normal request data
        n_samples = 1000
        n_features = 20
        
        # Generate normal traffic pattern
        X_normal = np.random.randn(n_samples, n_features) * 0.5 + 0.5
        
        # Normalize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_normal)
        
        # Train Isolation Forest
        # contamination: expected % of anomalies (5%)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        self.model.fit(X_scaled)
        
        # Save model
        model_path = f"{self.model_dir}/isolation_forest_v1.pkl"
        scaler_path = f"{self.model_dir}/scaler_v1.pkl"
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Model saved to {model_path}")
    
    def score_request(self, features: np.ndarray) -> Tuple[float, int]:
        """
        Score a request for anomalies
        
        Returns:
            anomaly_score: 0.0-1.0 (0=normal, 1=anomalous)
            prediction: -1 (anomaly) or 1 (normal)
        """
        
        if self.model is None or self.scaler is None:
            return 0.5, 1  # Return neutral score if model not ready
        
        try:
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get prediction (-1 = anomaly, 1 = normal)
            prediction = self.model.predict(features_scaled)[0]
            
            # Get anomaly score (negative of decision function)
            decision_score = self.model.score_samples(features_scaled)[0]
            
            # Normalize to 0-1 range
            # Decision scores are typically -1 to 0
            anomaly_score = max(0.0, min(1.0, -decision_score))
            
            return float(anomaly_score), int(prediction)
        
        except Exception as e:
            print(f"Error scoring request: {e}")
            return 0.5, 1


# Global model instance
_ml_manager = None

def get_ml_manager() -> MLModelManager:
    """Get or create ML model manager"""
    global _ml_manager
    if _ml_manager is None:
        _ml_manager = MLModelManager()
    return _ml_manager