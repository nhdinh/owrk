"""
Asset Management Service - Main Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.api.v1.router import api_router
from app.services.depreciation_service import DepreciationService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    logger.info(f"Scheduled depreciation calculation on day {settings.DEPRECIATION_DAY_OF_MONTH} of each month")


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

    # Start scheduler
    scheduler.start()
    schedule_depreciation_calculation()
    logger.info("Scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down Asset Management Service...")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
    )
