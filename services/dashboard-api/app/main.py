"""
Dashboard Service - Main Application
Provides centralized dashboard statistics and system health monitoring
"""

import asyncio
import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

import httpx

from app.core.config import settings
from app.core.rabbitmq import consume_events, rabbitmq
from app.core.database import connect_mongodb, close_mongodb, get_mongo_db
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno) - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Dashboard Service...")

    async with httpx.AsyncClient() as client:
        data = {
            "name": settings.SERVICE_NAME,
            "address": settings.SERVICE_ADDRESS,
            "port": settings.SERVICE_PORT,
            "health_endpoint": "/health",
        }
        headers = {"Content-Type": "application/json"}
        httpx.post("http://service-registry:3000/register", json=data)

    # log node id
    node_id_path = "node_id"
    node_id = None
    if not os.path.exists(node_id_path):
        node_id = str(uuid.uuid4())
        with open(node_id_path, "w+") as f:
            f.write(node_id)

        logger.info(f"✅ Node ID created: {node_id}")
    else:
        with open(node_id_path, "r") as f:
            node_id = f.read()

        logger.info(f"✅ Node ID exists: {node_id}")

    # Connect to MongoDB (for reading CQRS data if needed)
    try:
        await connect_mongodb()
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")

    # Connect to RabbitMQ
    try:
        await rabbitmq.connect()
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")

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
