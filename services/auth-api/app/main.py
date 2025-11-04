"""
Auth Service - Main Application
Handles authentication, authorization, MFA, and Active Directory integration
"""

import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

import httpx

from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.core.rabbitmq import rabbitmq, consume_events
from app.core.mongo_db import connect_mongo, close_mongo, get_mongo_db
from app.models.base import Base
from app.api.v1.router import api_router
from app.consumers.user_event_consumer import user_event_consumer
import asyncio

# Import Message Bus and Handlers
from app.core.message_bus import message_bus
from app.schemas.commands.user_commands import (
    CreateUserCommand,
    UpdateUserCommand,
    DeleteUserCommand,
    ActivateUserCommand,
    DeactivateUserCommand,
)
from app.schemas.queries.user_queries import (
    GetUserByIdQuery,
    GetUsersListQuery,
    GetUserHistoryQuery,
)
from app.commands.handlers import (
    CreateUserHandler,
    UpdateUserHandler,
    DeleteUserHandler,
    ActivateUserHandler,
    DeactivateUserHandler,
)
from app.queries.handlers import (
    GetUserByIdHandler,
    GetUsersListHandler,
    SearchUsersHandler,
    GetUserHistoryHandler,
)
from app.read_repositories.user_read_repository import UserReadRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# supress sqlalchemy logging
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)


async def register_cqrs_handlers():
    """
    Register all CQRS command and query handlers with the message bus
    This enables the CQRS pattern for all operations

    Note: Command handlers receive database session per request via dependency injection
    Query handlers use MongoDB repository
    """
    logger.info("📝 Registering CQRS handlers...")

    # Get MongoDB instance for query handlers
    mongo_db = get_mongo_db()
    user_read_repo = UserReadRepository(mongo_db)

    try:
        # Register Command Handlers (Write operations)
        # Handlers receive database session from endpoint via execute_command(command, db=db)
        message_bus.register_command_handler(CreateUserCommand, CreateUserHandler())
        message_bus.register_command_handler(UpdateUserCommand, UpdateUserHandler())
        message_bus.register_command_handler(DeleteUserCommand, DeleteUserHandler())
        message_bus.register_command_handler(ActivateUserCommand, ActivateUserHandler())
        message_bus.register_command_handler(
            DeactivateUserCommand, DeactivateUserHandler()
        )

        logger.info("✅ Command handlers registered")

        # Register Query Handlers (Read operations)
        message_bus.register_query_handler(
            GetUserByIdQuery, GetUserByIdHandler(user_read_repo)
        )
        message_bus.register_query_handler(
            GetUsersListQuery, GetUsersListHandler(user_read_repo)
        )
        message_bus.register_query_handler(
            GetUserHistoryQuery,
            GetUserHistoryHandler(),  # History handler needs db per request
        )

        logger.info("✅ Query handlers registered")
        logger.info("✅ CQRS handlers registration complete")

    except Exception as e:
        logger.error(f"❌ Failed to register handlers: {e}")
        raise


async def start_event_consumer():
    """
    Start consuming events from RabbitMQ
    Runs in background task
    """
    try:
        await consume_events(
            exchange_name="auth.events",
            queue_name="auth.read_model_updater",
            routing_keys=["user.*", "role.*"],
            callback=user_event_consumer.handle_event,
        )

        logger.info(f"Event consumer intialized.")
    except Exception as e:
        logger.error(f"❌ Event consumer error: {e}")
        # Retry after delay
        await asyncio.sleep(5)
        asyncio.create_task(start_event_consumer())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Auth Service...")

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
    node_id_path = "/tmp/node_id"
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

    # register service node

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

    # Register CQRS handlers
    try:
        await register_cqrs_handlers()
        logger.info("✅ CQRS handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register CQRS handlers: {e}")

    # Initialize event consumer
    try:
        await user_event_consumer.initialize()
        logger.info("✅ Event consumer initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize event consumer: {e}")

    # Start consuming events in background
    asyncio.create_task(start_event_consumer())
    logger.info("📥 Event consumer started in background")

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
    lifespan=lifespan,
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
    return {"status": "healthy", "service": "auth-service", "version": "1.0.0"}


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )
