"""
NexusAI - Intelligent Content & Code Generation Platform
A production-grade AI SaaS backend built with FastAPI
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine, Base
from app.api.v1 import router as api_v1_router
from app.middleware.rate_limit import RateLimitMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized")
    yield
    logger.info("🛑 Shutting down NexusAI...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## NexusAI — Intelligent Generation Platform 🚀

A production-ready AI SaaS API for content generation, code assistance, 
and intelligent data analysis. Built with **FastAPI**, **PostgreSQL**, 
**Redis**, and **OpenAI**.

### Features
- 🔐 JWT Authentication with role-based access control
- ⚡ Async-first architecture for maximum throughput
- 🤖 AI-powered generation (text, code, analysis)
- 🧠 Conversation memory with thread management
- 📊 Usage analytics and quota management
- 🔄 Background task processing with Celery
- 🛡️ Rate limiting per user/plan tier
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration:.2f}"
    return response


# ── Exception Handlers ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
