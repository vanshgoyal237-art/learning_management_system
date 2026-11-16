"""
Application configuration. All secrets come from environment variables
(copy .env.example to .env and `export` / load it) - never hard-code them.
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load settings from a local .env file when python-dotenv is installed, so the app
# works the same from `flask run`, `python app.py`, VS Code's debugger or a terminal.
# Real environment variables always win over the file.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env", override=False)
except ImportError:
    pass


class Config:
    # Required in production. The dev fallback is deliberately obvious.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # --- MySQL -----------------------------------------------------------------
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "lms_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "lms_ml")

    # --- Sessions / cookies ----------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"  # set 1 behind HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    # Same protections for the optional "keep me signed in" cookie.
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    # --- Uploads ---------------------------------------------------------------
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024   # 25 MB request cap

    # --- ML artifacts ----------------------------------------------------------
    ARTIFACT_DIR = BASE_DIR / "model" / "artifacts"
    # Don't re-write a prediction row (or its side effects) more often than this.
    ATTENDANCE_MIN_PCT = 75                   # usual college minimum; shown to students as the line to stay above
    PREDICTION_HISTORY_MIN_GAP_MINUTES = 60
    MANDATORY_REVIEW_DAYS = 3                 # At Risk -> review scheduled this many days ahead

    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
