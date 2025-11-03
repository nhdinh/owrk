"""
Dashboard Service - Main Application
Provides centralized dashboard statistics and system health monitoring
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import connect_mongodb, close_mongodb
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Dashboard Service...")

    # Connect to MongoDB (for reading CQRS data if needed)
    await connect_mongodb()

    logger.info("✅ Dashboard Service started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Dashboard Service...")
    await close_mongodb()
    logger.info("✅ Dashboard Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Dashboard Service API",
    description="Centralized dashboard for system statistics and monitoring",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Dashboard Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dashboard-api"}
