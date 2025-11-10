"""
Admin Management Service - Main Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Admin Service...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Start trash cleanup scheduler
    try:
        from app.tasks.trash_cleanup import start_scheduler, stop_scheduler
        start_scheduler()
        logger.info("Trash cleanup scheduler started")
    except Exception as e:
        logger.error(f"Error starting trash cleanup scheduler: {e}")

    logger.info("Admin Service started successfully")
    yield

    # Shutdown
    logger.info("Shutting down Admin Service...")
    try:
        stop_scheduler()
        logger.info("Trash cleanup scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping trash cleanup scheduler: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Admin Management Service API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME, "version": "1.0.0"}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include API routers
from app.api.v1.endpoints import module_settings, trash

app.include_router(module_settings.router, prefix=f"{settings.API_PREFIX}/admin/module-settings", tags=["Module Settings"])
app.include_router(trash.router, prefix=f"{settings.API_PREFIX}/admin/trash", tags=["Trash Management"])
