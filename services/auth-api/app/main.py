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
from app.services.permission_sync_service import permission_sync_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.read_repositories.user_read_repository import UserReadRepository
from app.core.service_discovery import register_service

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


async def initial_permission_sync():
    """Run initial permission sync after startup delay"""
    await asyncio.sleep(10)  # Wait 10 seconds for services to start
    logger.info("🔄 Running initial permission sync...")
    try:
        results = await permission_sync_service.sync_all_permissions()
        logger.info(f"✅ Initial permission sync complete: {results}")
    except Exception as e:
        logger.error(f"❌ Initial permission sync failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Auth Service...")

    # Register with service registry
    await register_service()

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
    # try:
    #     Base.metadata.create_all(bind=engine)
    #     logger.info("✅ Database tables created")
    # except Exception as e:
    #     logger.error(f"❌ Failed to create database tables: {e}")

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

    # Start permission sync scheduler
    scheduler = AsyncIOScheduler()

    # Schedule permission sync every 5 minutes
    scheduler.add_job(
        permission_sync_service.sync_all_permissions,
        'interval',
        minutes=5,
        id='permission_sync',
        name='Sync permissions from all services',
        replace_existing=True
    )

    scheduler.start()
    logger.info("📅 Permission sync scheduler started (every 5 minutes)")

    # Run initial sync after 10 seconds
    asyncio.create_task(initial_permission_sync())

    logger.info("✅ Auth Service started successfully")

    yield

    # Shutdown scheduler
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Permission sync scheduler stopped")

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


@app.get("/permissions")
async def get_service_permissions():
    """
    Get all permissions owned by auth-api for permission discovery.

    This endpoint is used by the permission sync service to discover
    and sync permissions from this service.
    """
    AUTH_PERMISSIONS = [
        {
            "code": "user:create",
            "name": "Create Users",
            "resource": "user",
            "action": "create",
            "description": "Create new user accounts in the system",
        },
        {
            "code": "user:read",
            "name": "View Users",
            "resource": "user",
            "action": "read",
            "description": "View user account details and list users",
        },
        {
            "code": "user:update",
            "name": "Update Users",
            "resource": "user",
            "action": "update",
            "description": "Modify existing user accounts",
        },
        {
            "code": "user:delete",
            "name": "Delete Users",
            "resource": "user",
            "action": "delete",
            "description": "Remove user accounts from the system",
        },
        {
            "code": "role:create",
            "name": "Create Roles",
            "resource": "role",
            "action": "create",
            "description": "Create new roles for access control",
        },
        {
            "code": "role:read",
            "name": "View Roles",
            "resource": "role",
            "action": "read",
            "description": "View role details and list roles",
        },
        {
            "code": "role:update",
            "name": "Update Roles",
            "resource": "role",
            "action": "update",
            "description": "Modify existing roles and their permissions",
        },
        {
            "code": "role:delete",
            "name": "Delete Roles",
            "resource": "role",
            "action": "delete",
            "description": "Remove roles from the system",
        },
        {
            "code": "permission:read",
            "name": "View Permissions",
            "resource": "permission",
            "action": "read",
            "description": "View available permissions in the system",
        },
        {
            "code": "permission:assign",
            "name": "Assign Permissions",
            "resource": "permission",
            "action": "assign",
            "description": "Assign permissions to roles",
        },
        {
            "code": "auth:login",
            "name": "User Authentication",
            "resource": "auth",
            "action": "login",
            "description": "Authenticate users and generate tokens",
        },
        {
            "code": "auth:mfa",
            "name": "Multi-Factor Authentication",
            "resource": "auth",
            "action": "mfa",
            "description": "Manage MFA settings and verification",
        },
    ]

    return {
        "service": "auth-api",
        "version": "1.0.0",
        "description": "Authentication and Authorization Service",
        "permissions": AUTH_PERMISSIONS,
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
