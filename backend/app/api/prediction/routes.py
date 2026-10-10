from datetime import datetime, timezone
import pickle

from bson import ObjectId
from flask import Blueprint, g, jsonify, request

from ...core.security import auth_required
from ...database.connection import get_database
from ...ml_engine.preprocessing import validate_input
from ...ml_engine.predictor import HeartPredictor

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/prediction")
predictor = None


def get_predictor():
    global predictor
    if predictor is None:
        predictor = HeartPredictor()
    return predictor


@prediction_bp.post("/heart")
@auth_required
def predict_heart():
    try:
        values = validate_input(request.get_json(silent=True))
        result = get_predictor().predict(values)
    except (ValueError, FileNotFoundError, OSError, pickle.UnpicklingError) as error:
        return jsonify(success=False, error="Invalid input" if isinstance(error, ValueError) else "Prediction service unavailable", details=str(error) if isinstance(error, ValueError) else None), 400 if isinstance(error, ValueError) else 503
    record = {**values, **result, "user_id": ObjectId(g.user_id), "disease": "heart_disease", "model_name": type(get_predictor().model).__name__, "model_version": "1.0", "created_at": datetime.now(timezone.utc)}
    database = get_database()
    inserted = database.predictions.insert_one(record)
    result.update({"success": True, "id": str(inserted.inserted_id), "disease": "heart_disease", "message": "This is an educational risk estimate, not a medical diagnosis. Please consult a qualified healthcare professional."})
    return jsonify(result), 201


@prediction_bp.get("/history")
@auth_required
def history():
    database = get_database()
    records = []
    for item in database.predictions.find({"user_id": ObjectId(g.user_id)}).sort("created_at", -1):
        item["id"] = str(item.pop("_id"))
        item["user_id"] = str(item["user_id"])
        item["created_at"] = item["created_at"].isoformat() if hasattr(item["created_at"], "isoformat") else item["created_at"]
        records.append(item)
    return jsonify(success=True, predictions=records)


@prediction_bp.get("/<prediction_id>")
@auth_required
def prediction_detail(prediction_id):
    database = get_database()
    try:
        item = database.predictions.find_one({"_id": ObjectId(prediction_id), "user_id": ObjectId(g.user_id)})
    except Exception:
        item = None
    if not item:
        return jsonify(success=False, error="Prediction not found"), 404
    item["id"] = str(item.pop("_id"))
    item["created_at"] = item["created_at"].isoformat() if hasattr(item["created_at"], "isoformat") else item["created_at"]
    return jsonify(success=True, prediction=item)