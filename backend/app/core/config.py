import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(PROJECT_ROOT / "models" / "heart_model.pkl")))
SCALER_PATH = Path(os.getenv("SCALER_PATH", str(PROJECT_ROOT / "models" / "scaler.pkl")))
if not MODEL_PATH.is_absolute():
    MODEL_PATH = PROJECT_ROOT / MODEL_PATH
if not SCALER_PATH.is_absolute():
    SCALER_PATH = PROJECT_ROOT / SCALER_PATH
MONGO_URI = os.getenv("MONGO_URI", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "heart_risk_db")
SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
LOW_RISK_MAX = float(os.getenv("LOW_RISK_MAX", "0.39"))
MEDIUM_RISK_MAX = float(os.getenv("MEDIUM_RISK_MAX", "0.69"))