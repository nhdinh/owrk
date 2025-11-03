"""
Procurement Management Service - Main Application
FastAPI application for procurement operations
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.events import startup_event_publisher, shutdown_event_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Procurement Service...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Initialize event publisher
    try:
        startup_event_publisher()
    except Exception as e:
        logger.warning(f"Event publisher initialization failed: {e}")

    logger.info("Procurement Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Procurement Service...")
    shutdown_event_publisher()
    logger.info("Procurement Service shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Procurement Management Service API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    """
    Health check endpoint
    Returns service status
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    Returns service information
    """
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include API routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.DEBUG
    )
