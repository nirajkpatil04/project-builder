"""Application configuration.

All settings come from environment variables (optionally loaded from backend/.env),
so the same build can run locally, in Docker or in the cloud without code changes.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

INSECURE_DEFAULT_SECRET = "dev-insecure-secret-change-me-in-production"


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Project Builder")
        self.version = "1.0.0"
        self.env = os.getenv("APP_ENV", "development")

        # Database
        if os.getenv("VERCEL"):
            default_db = "/tmp/project_builder.db"
        else:
            default_db = (BASE_DIR / "data" / "project_builder.db").as_posix()
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")

        # Auth
        self.jwt_secret = os.getenv("JWT_SECRET", INSECURE_DEFAULT_SECRET)
        self.jwt_algorithm = "HS256"
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "720"))
        self.bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@projectbuilder.dev").lower()
        self.admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
        self.admin_name = os.getenv("ADMIN_NAME", "Platform Admin")

        # CORS
        default_origins = "http://localhost:5173,http://127.0.0.1:5173,*" if os.getenv("VERCEL") else "http://localhost:5173,http://127.0.0.1:5173"
        origins = os.getenv("CORS_ORIGINS", default_origins)
        self.cors_origins = [o.strip() for o in origins.split(",") if o.strip()]

        # Generative AI (optional)
        self.llm_provider = os.getenv("LLM_PROVIDER", "auto").lower()  # auto | gemini | openai | none
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.llm_timeout = float(os.getenv("LLM_TIMEOUT", "45"))

        # File / cloud storage
        self.storage_backend = os.getenv("STORAGE_BACKEND", "local").lower()  # local | s3
        self.storage_dir = Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "data" / "uploads")))
        self.s3_bucket = os.getenv("S3_BUCKET", "")
        self.s3_region = os.getenv("S3_REGION", "ap-south-1")
        self.s3_endpoint = os.getenv("S3_ENDPOINT_URL", "") or None
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "10"))

        # Abuse protection
        self.rate_limit_enabled = _bool("RATE_LIMIT_ENABLED", True)
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "240"))
        self.auth_rate_limit_per_minute = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "10"))

        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"

    def validate(self) -> None:
        if self.is_production and self.jwt_secret == INSECURE_DEFAULT_SECRET:
            raise RuntimeError("JWT_SECRET must be set to a strong random value in production.")
        if self.is_production and self.admin_password == "Admin@12345":
            raise RuntimeError("ADMIN_PASSWORD must be changed in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
