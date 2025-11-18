"""
Procurement Management Service - Main Application
FastAPI application for procurement operations
"""

import logging
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.events import startup_event_publisher, shutdown_event_publisher
from app.core.service_discovery import register_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
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

    # Register with service registry
    await register_service()

    # Create database tables
    # try:
    #     Base.metadata.create_all(bind=engine)
    #     logger.info("Database tables created successfully")
    # except Exception as e:
    #     logger.error(f"Error creating database tables: {e}")

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
    """
    Health check endpoint
    Returns service status
    """
    return {"status": "healthy", "service": settings.APP_NAME, "version": "1.0.0"}


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
        "health": "/health",
    }


@app.get("/permissions", tags=["Permissions"])
async def get_service_permissions():
    """
    Get all permissions owned by procurement-api for permission discovery.

    This endpoint is used by the permission sync service to discover
    and sync permissions from this service.
    """
    PROCUREMENT_PERMISSIONS = [
        {
            "code": "vendor:create",
            "name": "Create Vendors",
            "resource": "vendor",
            "action": "create",
            "description": "Create new vendor accounts",
        },
        {
            "code": "vendor:read",
            "name": "View Vendors",
            "resource": "vendor",
            "action": "read",
            "description": "View vendor details and list vendors",
        },
        {
            "code": "vendor:update",
            "name": "Update Vendors",
            "resource": "vendor",
            "action": "update",
            "description": "Modify existing vendor information",
        },
        {
            "code": "vendor:delete",
            "name": "Delete Vendors",
            "resource": "vendor",
            "action": "delete",
            "description": "Remove vendors from the system",
        },
        {
            "code": "purchase_request:create",
            "name": "Create Purchase Requests",
            "resource": "purchase_request",
            "action": "create",
            "description": "Create new purchase requests",
        },
        {
            "code": "purchase_request:read",
            "name": "View Purchase Requests",
            "resource": "purchase_request",
            "action": "read",
            "description": "View purchase request details and list requests",
        },
        {
            "code": "purchase_request:update",
            "name": "Update Purchase Requests",
            "resource": "purchase_request",
            "action": "update",
            "description": "Modify existing purchase requests",
        },
        {
            "code": "purchase_request:delete",
            "name": "Delete Purchase Requests",
            "resource": "purchase_request",
            "action": "delete",
            "description": "Remove purchase requests from the system",
        },
        {
            "code": "purchase_request:approve",
            "name": "Approve Purchase Requests",
            "resource": "purchase_request",
            "action": "approve",
            "description": "Approve or reject purchase requests",
        },
        {
            "code": "purchase_order:create",
            "name": "Create Purchase Orders",
            "resource": "purchase_order",
            "action": "create",
            "description": "Create new purchase orders",
        },
        {
            "code": "purchase_order:read",
            "name": "View Purchase Orders",
            "resource": "purchase_order",
            "action": "read",
            "description": "View purchase order details and list orders",
        },
        {
            "code": "purchase_order:update",
            "name": "Update Purchase Orders",
            "resource": "purchase_order",
            "action": "update",
            "description": "Modify existing purchase orders",
        },
        {
            "code": "purchase_order:delete",
            "name": "Delete Purchase Orders",
            "resource": "purchase_order",
            "action": "delete",
            "description": "Remove purchase orders from the system",
        },
        {
            "code": "purchase_order:approve",
            "name": "Approve Purchase Orders",
            "resource": "purchase_order",
            "action": "approve",
            "description": "Approve or reject purchase orders",
        },
        {
            "code": "budget:read",
            "name": "View Budgets",
            "resource": "budget",
            "action": "read",
            "description": "View budget allocations and spending",
        },
        {
            "code": "budget:manage",
            "name": "Manage Budgets",
            "resource": "budget",
            "action": "manage",
            "description": "Create and modify budget allocations",
        },
    ]

    return {
        "service": "procurement-api",
        "version": "1.0.0",
        "description": "Procurement Management Service",
        "permissions": PROCUREMENT_PERMISSIONS,
    }


# Import and include API routers
from app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")
