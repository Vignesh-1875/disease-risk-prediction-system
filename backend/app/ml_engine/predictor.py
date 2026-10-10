from ..core.config import LOW_RISK_MAX, MEDIUM_RISK_MAX, MODEL_PATH, SCALER_PATH
from .preprocessing import FEATURES, to_vector
import joblib


class HeartPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict(self, values):
        vector = self.scaler.transform(to_vector(values))
        prediction = int(self.model.predict(vector)[0])
        if hasattr(self.model, "predict_proba"):
            probability = float(self.model.predict_proba(vector)[0][1])
        else:
            probability = float(prediction)
        if probability <= LOW_RISK_MAX:
            risk_level = "Low"
        elif probability <= MEDIUM_RISK_MAX:
            risk_level = "Medium"
        else:
            risk_level = "High"
        importance = getattr(self.model, "feature_importances_", None)
        factors = []
        if importance is not None:
            factors = [
                name for _, name in sorted(
                    zip(importance, FEATURES), reverse=True
                )[:5]
            ]
        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_level": risk_level,
            "important_factors": factors,
        }