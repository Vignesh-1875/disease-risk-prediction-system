from datetime import datetime, timezone
import sqlite3

from bson import ObjectId
from flask import Blueprint, g, jsonify, request
from pymongo.errors import DuplicateKeyError

from ...core.security import auth_required, create_token, hash_password, verify_password
from ...database.connection import get_database

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("password", "")
    if not name or "@" not in email or len(password) < 8:
        return jsonify(success=False, error="Name, valid email, and password of at least 8 characters are required"), 400
    database = get_database()
    try:
        result = database.users.insert_one({"name": name, "email": email, "password_hash": hash_password(password), "created_at": datetime.now(timezone.utc)})
    except (DuplicateKeyError, sqlite3.IntegrityError):
        return jsonify(success=False, error="Email is already registered"), 409
    return jsonify(success=True, user_id=str(result.inserted_id)), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    database = get_database()
    user = database.users.find_one({"email": str(data.get("email", "")).lower()})
    if user is None or not verify_password(data.get("password", ""), user["password_hash"]):
        return jsonify(success=False, error="Invalid email or password"), 401
    return jsonify(success=True, token=create_token(str(user["_id"])), user={"id": str(user["_id"]), "name": user["name"], "email": user["email"]})


@auth_bp.post("/logout")
@auth_required
def logout():
    return jsonify(success=True, message="Logged out successfully")


@auth_bp.get("/me")
@auth_required
def me():
    database = get_database()
    user = database.users.find_one({"_id": ObjectId(g.user_id)}, {"password_hash": 0})
    if user is None:
        return jsonify(success=False, error="User not found"), 404
    user["id"] = str(user.pop("_id"))
    return jsonify(success=True, user=user)