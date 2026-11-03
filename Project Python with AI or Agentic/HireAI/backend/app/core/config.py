"""Centralized application settings for HireAI."""

import os
from pathlib import Path
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve root directory: if frozen (.exe), use directory of executable; otherwise project root
if getattr(sys, "frozen", False):
    _PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_ROOT_STORAGE = _PROJECT_ROOT / "storage"


class Settings(BaseSettings):
    """Application settings schema reading from environment and .env file."""

    APP_NAME: str = "HireAI – Intelligent Recruitment & Assessment Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # Security & JWT Authentication
    SECRET_KEY: str = "hireai-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Origins
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:8000,tauri://localhost,*"

    # Storage Paths at project root
    PROJECT_ROOT: Path = _PROJECT_ROOT
    STORAGE_DIR: Path = _ROOT_STORAGE
    RESUME_STORAGE_DIR: Path = _ROOT_STORAGE / "resumes"
    JOB_STORAGE_DIR: Path = _ROOT_STORAGE / "job_descriptions"
    REPORT_STORAGE_DIR: Path = _ROOT_STORAGE / "reports"
    SUBMISSION_STORAGE_DIR: Path = _ROOT_STORAGE / "submissions"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_ROOT_STORAGE.as_posix()}/hireai.db",
    )

    # Redis for Celery & caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Uploads
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_FILE_EXTENSIONS: str = "pdf,docx,doc,txt,rtf"

    # AI Models & Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    # Code Execution Worker Limits
    CODE_EXEC_TIMEOUT_SECONDS: int = 5
    CODE_EXEC_MEMORY_MB: int = 128
    DOCKER_SANDBOX_ENABLED: bool = os.getenv("DOCKER_SANDBOX_ENABLED", "false").lower() == "true"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
