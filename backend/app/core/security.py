from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .config import JWT_EXPIRES_HOURS, SECRET_KEY


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def create_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_HOURS)
    return jwt.encode({"sub": user_id, "exp": expires}, SECRET_KEY, algorithm="HS256")


def auth_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(success=False, error="Authentication required"), 401
        try:
            payload = jwt.decode(header[7:], SECRET_KEY, algorithms=["HS256"])
            g.user_id = payload["sub"]
        except (jwt.InvalidTokenError, KeyError):
            return jsonify(success=False, error="Invalid or expired token"), 401
        return handler(*args, **kwargs)

    return wrapper