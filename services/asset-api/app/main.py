"""
Asset Management Service - Main Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.api.v1.router import api_router
from app.services.depreciation_service import DepreciationService
from app.core.service_discovery import register_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


def schedule_depreciation_calculation():
    """Schedule monthly depreciation calculation"""
    # Run on the configured day of month at 00:00
    scheduler.add_job(
        run_depreciation_calculation,
        CronTrigger(day=settings.DEPRECIATION_DAY_OF_MONTH, hour=0, minute=0),
        id="monthly_depreciation",
        replace_existing=True,
    )
    logger.info(
        f"Scheduled depreciation calculation on day {settings.DEPRECIATION_DAY_OF_MONTH} of each month"
    )


def run_depreciation_calculation():
    """Run depreciation calculation"""
    try:
        period_month = DepreciationService.get_current_period()
        count = DepreciationService.calculate_all_depreciation(period_month)
        logger.info(f"Depreciation calculation completed: {count} assets processed")
    except Exception as e:
        logger.error(f"Error in depreciation calculation: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Asset Management Service...")

    # Register with service registry
    await register_service()

    # Start scheduler only if not in testing mode
    if not settings.TESTING:
        scheduler.start()
        schedule_depreciation_calculation()
        logger.info("Scheduler started")
    else:
        logger.info("Scheduler disabled (TESTING mode)")

    yield

    # Shutdown
    logger.info("Shutting down Asset Management Service...")
    if not settings.TESTING:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="Asset Management Service",
    description="API for managing organizational assets, assignments, and depreciation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "asset-api",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Asset Management Service API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/permissions")
async def get_service_permissions():
    """
    Get all permissions owned by asset-api for permission discovery.

    This endpoint is used by the permission sync service to discover
    and sync permissions from this service.
    """
    ASSET_PERMISSIONS = [
        {
            "code": "asset:create",
            "name": "Create Assets",
            "resource": "asset",
            "action": "create",
            "description": "Create new assets in the system",
        },
        {
            "code": "asset:read",
            "name": "View Assets",
            "resource": "asset",
            "action": "read",
            "description": "View asset details and list assets",
        },
        {
            "code": "asset:update",
            "name": "Update Assets",
            "resource": "asset",
            "action": "update",
            "description": "Modify existing asset information",
        },
        {
            "code": "asset:delete",
            "name": "Delete Assets",
            "resource": "asset",
            "action": "delete",
            "description": "Remove assets from the system",
        },
        {
            "code": "asset:assign",
            "name": "Assign Assets",
            "resource": "asset",
            "action": "assign",
            "description": "Assign assets to users or locations",
        },
        {
            "code": "asset:transfer",
            "name": "Transfer Assets",
            "resource": "asset",
            "action": "transfer",
            "description": "Transfer assets between users or locations",
        },
        {
            "code": "asset:maintain",
            "name": "Maintain Assets",
            "resource": "asset",
            "action": "maintain",
            "description": "Record asset maintenance activities",
        },
        {
            "code": "category:create",
            "name": "Create Categories",
            "resource": "category",
            "action": "create",
            "description": "Create new asset categories",
        },
        {
            "code": "category:read",
            "name": "View Categories",
            "resource": "category",
            "action": "read",
            "description": "View category details and list categories",
        },
        {
            "code": "category:update",
            "name": "Update Categories",
            "resource": "category",
            "action": "update",
            "description": "Modify existing categories",
        },
        {
            "code": "category:delete",
            "name": "Delete Categories",
            "resource": "category",
            "action": "delete",
            "description": "Remove categories from the system",
        },
        {
            "code": "depreciation:read",
            "name": "View Depreciation",
            "resource": "depreciation",
            "action": "read",
            "description": "View depreciation records and schedules",
        },
        {
            "code": "depreciation:calculate",
            "name": "Calculate Depreciation",
            "resource": "depreciation",
            "action": "calculate",
            "description": "Trigger depreciation calculations",
        },
    ]

    return {
        "service": "asset-api",
        "version": "1.0.0",
        "description": "Asset Management Service",
        "permissions": ASSET_PERMISSIONS,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
    )
