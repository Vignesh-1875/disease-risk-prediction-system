from flask import Flask, jsonify
from flask_cors import CORS

from .api.auth.routes import auth_bp
from .api.history.routes import history_bp
from .api.prediction.routes import prediction_bp
from .api.user.routes import user_bp
from .core.config import FRONTEND_ORIGIN
from .database.connection import init_database


def create_app(connect_database=True):
    app = Flask(__name__)
    CORS(app, origins=FRONTEND_ORIGIN)
    if connect_database:
        init_database()
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(history_bp)

    @app.get("/api/health")
    def health():
        return jsonify(success=True, service="heart-risk-api")

    return app