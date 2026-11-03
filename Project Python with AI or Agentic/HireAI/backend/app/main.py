"""HireAI — FastAPI Application Entry Point.

Intelligent Recruitment & Technical Assessment Platform.
Handles resume screening, JD matching, skill-gap analysis,
isolated technical assessments, and AI interviewer copilot.
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import sys

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.database.connection import init_db

# Setup centralized logging
setup_logging()
logger = logging.getLogger(__name__)

# Locate static directory supporting frozen single-file bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    STATIC_DIR = Path(sys._MEIPASS) / "backend" / "app" / "static"
    if not STATIC_DIR.exists():
        STATIC_DIR = Path(sys._MEIPASS) / "app" / "static"
else:
    STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown routines."""
    logger.info("Starting %s in %s environment...", settings.APP_NAME, settings.APP_ENV)

    # Ensure storage directories exist
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.JOB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.REPORT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.SUBMISSION_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database tables and seed default questions
    logger.info("Initializing database tables...")
    init_db()

    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Technical Recruitment & Assessment Platform with Isolated Code Execution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Parse allowed origins
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized exception handlers
register_exception_handlers(app)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount versioned API
app.include_router(api_v1_router)


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the interactive web interface."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "application": settings.APP_NAME,
        "docs_url": "/docs",
        "api_v1": "/api/v1/health",
    }
