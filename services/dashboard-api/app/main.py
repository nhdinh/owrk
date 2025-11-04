"""
Dashboard Service - Main Application
Provides centralized dashboard statistics and system health monitoring
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.message_bus import message_bus
from app.core.rabbitmq import consume_events, rabbitmq
from app.core.database import connect_mongodb, close_mongodb, get_mongo_db
from app.api.v1.router import api_router
from app.read_repositories.service_read_repository import ServiceReadRepository
from app.consumers.service_event_consumer import service_event_consumer

from app.schemas.queries.service_query import GetServicesListQuery
from app.schemas.commands.service_commands import RegisterServiceCommand
from app.queries.handlers import GetServicesListQueryHandler
from app.commands.handlers import RegisterServiceCommandHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


def schedule_ping_service_availability():
    # TODO: Implement configured job to ping for service healths
    pass


async def register_cqrs_handlers():
    """
    Register all CQRS command and query handlers with the message bus
    This enables the CQRS pattern for all operations

    Note: Command handlers receive database session per request via dependency injection
    Query handlers use MongoDB repository
    """
    logger.info("📝 Registering CQRS handlers...")

    mongo_db = get_mongo_db()
    service_read_repo = ServiceReadRepository(mongo_db)

    try:
        # Register command handler
        message_bus.register_command_handler(
            RegisterServiceCommand, RegisterServiceCommandHandler()
        )
        logger.info("✅ Command handlers registered")

        # Register query handler
        message_bus.register_query_handler(
            GetServicesListQuery, GetServicesListQueryHandler(service_read_repo)
        )

        logger.info("✅ Query handlers registered")
        logger.info("✅ CQRS handlers registration complete")
    except Exception as e:
        logger.error(f"❌ Failed to register handlers: {e}")
        raise


async def start_event_consumer():
    """
    Start consuming events from RabbitMQ in background task
    """
    try:
        await consume_events(
            exchange_name="registry.events",
            queue_name="registry.read_model_updater",
            routing_keys=[],
            callback=service_event_consumer.handle_event,
        )

        logger.info(f"Service Event consumer intialized.")
    except Exception as e:
        logger.error(f"❌ Service Event consumer error: {e}")
        # Retry after delay
        await asyncio.sleep(5)
        asyncio.create_task(start_event_consumer())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Dashboard Service...")

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

    # Register CQRS handlers
    try:
        await register_cqrs_handlers()
        logger.info("✅ CQRS handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register CQRS handlers: {e}")

    # Initialize event consumer
    try:
        await service_event_consumer.initialize()
        logger.info("✅ Event consumer initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize event consumer: {e}")

    # Start consuming events in background
    asyncio.create_task(start_event_consumer())
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
