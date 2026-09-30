import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "bfsi-prod-ready-secret-key-personal-finance-2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'finance.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

    # Session security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in production HTTPS environments
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # Financial Configuration
    DEFAULT_CURRENCY = "INR"
    CURRENCY_SYMBOL = "₹"
