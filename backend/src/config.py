"""Central configuration loaded from environment variables (.env supported)."""
from __future__ import annotations

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    # --- JWT -------------------------------------------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))
    )

    # --- Server ----------------------------------------------------------
    HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_RUN_PORT", "3001"))

    # --- CORS ------------------------------------------------------------
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]

    # --- Demo seed -------------------------------------------------------
    SEED_DEMO_USER = _as_bool(os.getenv("SEED_DEMO_USER"), default=True)
    DEMO_EMAIL = os.getenv("DEMO_EMAIL", "test")
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "test")

    # --- Database --------------------------------------------------------
    DB_PATH = os.getenv(
        "DB_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db"),
    )

    # --- CompreFace (optional) ------------------------------------------
    COMPREFACE_URL = os.getenv("COMPREFACE_URL", "").rstrip("/")
    COMPREFACE_API_KEY = os.getenv("COMPREFACE_API_KEY", "")
    FACE_SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD", "0.95"))

    @classmethod
    def face_enabled(cls) -> bool:
        return bool(cls.COMPREFACE_URL and cls.COMPREFACE_API_KEY)
