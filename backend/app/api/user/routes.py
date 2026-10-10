from bson import ObjectId
from flask import Blueprint, g, jsonify, request

from ...core.security import auth_required
from ...database.connection import get_database

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.get("/profile")
@auth_required
def profile():
    database = get_database()
    user = database.users.find_one({"_id": ObjectId(g.user_id)}, {"password_hash": 0}) if database else None
    if not user:
        return jsonify(success=False, error="User not found"), 404
    user["id"] = str(user.pop("_id"))
    return jsonify(success=True, user=user)


@user_bp.put("/profile")
@auth_required
def update_profile():
    data = request.get_json(silent=True) or {}
    updates = {key: data[key].strip() for key in ("name",) if isinstance(data.get(key), str) and data[key].strip()}
    database = get_database()
    if not updates or database is None:
        return jsonify(success=False, error="No valid profile fields provided"), 400
    database.users.update_one({"_id": ObjectId(g.user_id)}, {"$set": updates})
    return jsonify(success=True)