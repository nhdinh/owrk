"""
Auth Service - Main Application
Handles authentication, authorization, MFA, and Active Directory integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine
from app.core.rabbitmq import rabbitmq
from app.core.mongo_db import connect_mongo, close_mongo
from app.models.base import Base
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Auth Service...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")

    # Connect to MongoDB
    try:
        await connect_mongo()
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")

    # Connect to RabbitMQ
    try:
        await rabbitmq.connect()
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")

    logger.info("✅ Auth Service started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Auth Service...")

    # Close MongoDB connection
    try:
        await close_mongo()
        logger.info("✅ MongoDB connection closed")
    except Exception as e:
        logger.error(f"❌ Failed to close MongoDB: {e}")

    # Close RabbitMQ connection
    try:
        await rabbitmq.close()
        logger.info("✅ RabbitMQ connection closed")
    except Exception as e:
        logger.error(f"❌ Failed to close RabbitMQ: {e}")

    logger.info("✅ Auth Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Asset Management - Auth Service",
    description="Authentication and Authorization Service with MFA and Active Directory support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration
    """
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
