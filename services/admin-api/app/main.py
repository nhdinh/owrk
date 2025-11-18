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
from app.core.service_discovery import register_service

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

    # Register with service registry
    await register_service()

    # Create database tables
    # try:
    #     Base.metadata.create_all(bind=engine)
    #     logger.info("Database tables created successfully")
    # except Exception as e:
    #     logger.error(f"Error creating database tables: {e}")

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


@app.get("/permissions", tags=["Permissions"])
async def get_service_permissions():
    """
    Get all permissions owned by admin-api for permission discovery.

    This endpoint is used by the permission sync service to discover
    and sync permissions from this service.
    """
    ADMIN_PERMISSIONS = [
        {
            "code": "module_settings:create",
            "name": "Create Module Settings",
            "resource": "module_settings",
            "action": "create",
            "description": "Create new module configuration settings",
        },
        {
            "code": "module_settings:read",
            "name": "View Module Settings",
            "resource": "module_settings",
            "action": "read",
            "description": "View module settings and configurations",
        },
        {
            "code": "module_settings:update",
            "name": "Update Module Settings",
            "resource": "module_settings",
            "action": "update",
            "description": "Modify module settings and configurations",
        },
        {
            "code": "module_settings:delete",
            "name": "Delete Module Settings",
            "resource": "module_settings",
            "action": "delete",
            "description": "Remove module settings",
        },
        {
            "code": "trash:read",
            "name": "View Trash",
            "resource": "trash",
            "action": "read",
            "description": "View deleted items in trash/recycle bin",
        },
        {
            "code": "trash:restore",
            "name": "Restore from Trash",
            "resource": "trash",
            "action": "restore",
            "description": "Restore items from trash",
        },
        {
            "code": "trash:delete",
            "name": "Permanently Delete",
            "resource": "trash",
            "action": "delete",
            "description": "Permanently delete items from trash",
        },
        {
            "code": "trash:manage",
            "name": "Manage Trash Settings",
            "resource": "trash",
            "action": "manage",
            "description": "Configure trash retention policies and auto-cleanup",
        },
        {
            "code": "audit_log:read",
            "name": "View Audit Logs",
            "resource": "audit_log",
            "action": "read",
            "description": "View system audit logs and activity history",
        },
        {
            "code": "system_log:read",
            "name": "View System Logs",
            "resource": "system_log",
            "action": "read",
            "description": "View system logs and error messages",
        },
        {
            "code": "system:configure",
            "name": "Configure System",
            "resource": "system",
            "action": "configure",
            "description": "Configure system-wide settings and parameters",
        },
    ]

    return {
        "service": "admin-api",
        "version": "1.0.0",
        "description": "Admin Management Service",
        "permissions": ADMIN_PERMISSIONS,
    }


# Import and include API routers
from app.api.v1.endpoints import module_settings, trash

app.include_router(
    module_settings.router,
    prefix=f"{settings.API_PREFIX}/admin/module-settings",
    tags=["Module Settings"],
)
app.include_router(
    trash.router, prefix=f"{settings.API_PREFIX}/admin/trash", tags=["Trash Management"]
)
