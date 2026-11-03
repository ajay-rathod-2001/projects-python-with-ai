from contextlib import asynccontextmanager
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import (
    WorkOSBaseException,
    workos_exception_handler,
    unhandled_exception_handler,
)
from app.database.redis import init_redis_pool, close_redis_pool
import app.database.session as session_module
from app.database.base import Base
from app.api.v1.router import api_router
from app.api.websockets.router import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for setup and teardown."""
    setup_logging()
    logger.info("Initializing WorkOS AI application services...")
    
    # 1. Initialize Redis (with graceful fallback)
    await init_redis_pool()

    # 2. Initialize Database with automatic SQLite fallback if PostgreSQL is not running
    try:
        async with session_module.engine.begin() as conn:
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except Exception:
                pass
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas verified and initialized.")
    except Exception as e:
        logger.warning(f"Primary database connection unavailable ({e}). Switching to local SQLite database for standalone mode.")
        fallback_url = "sqlite+aiosqlite:///./workos_local.db"
        session_module.engine = create_async_engine(
            fallback_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )
        session_module.async_session_factory.configure(bind=session_module.engine)
        async with session_module.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Local SQLite database initialized successfully (workos_local.db).")

    yield

    # Teardown
    logger.info("Shutting down WorkOS AI services...")
    await close_redis_pool()
    if session_module.engine:
        await session_module.engine.dispose()
    logger.info("WorkOS AI services cleanly stopped.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Tenant AI Operating System for Teams",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_and_timing_middleware(request: Request, call_next):
    """Injects a unique request correlation ID and measures request execution time."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    return response


# Centralized Exception Handlers
app.add_exception_handler(WorkOSBaseException, workos_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR, tags=["WebSockets"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check probe for container orchestrators and monitoring tools."""
    return {
        "status": "healthy",
        "service": "workos-ai-backend",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
