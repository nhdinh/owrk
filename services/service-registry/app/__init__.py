import asyncio
from contextlib import asynccontextmanager
import json
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


def ping_services():
    pass


async def schedule_services_pinging():
    """Schedule service pinging"""
    poll_duration = 5
    scheduler.add_job(
        ping_services,
        CronTrigger(minute=poll_duration),
        id="services_ping",
        replace_existing=True,
    )
    logger.info(f"Scheduled pinging services status every {poll_duration} minutes")


async def load_services():
    service_file_path = "/tmp/service.json"
    if not os.path.exists(service_file_path):
        services = json.dumps({})
        with open(service_file_path, "w+") as f:
            f.write(services)
    else:
        services = None
        with open(service_file_path, "r") as f:
            services = json.loads(f.read())

    return services


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Registry Service...")

    # Start scheduler for service pinging
    scheduler.start()
    await schedule_services_pinging()
    logger.info("Scheduler started")

    yield

    logger.info("✅ Registry Service shutdown complete")


app = FastAPI(
    title="Registry Service API",
    description="Centralized service for system statistics and monitoring",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/register")
async def register_service():
    pass


@app.get("/services")
async def get_services():
    return load_services(), 200


@app.get("/services/<service_id:str>")
async def get_service(service_id: str):
    return load_services()


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "service-registry-api"}
