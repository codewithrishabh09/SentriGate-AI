# app/ml/model_loader.py
from sklearn.ensemble import IsolationForest
import joblib
import os

def load_or_train_model():
    model_path = "/models/isolation_forest_v1.pkl"
    
    if os.path.exists(model_path):
        # Load pre-trained model
        model = joblib.load(model_path)
    else:
        # Train new model
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,  # Expect 5% anomalies
            random_state=42
        )
        # Train on historical data
        X_train = load_historical_data()
        model.fit(X_train)
        joblib.dump(model, model_path)
    
    return model