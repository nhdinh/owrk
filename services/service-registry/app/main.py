import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .schema import *
from .data import load_services, save_services, reset_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno) - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


async def ping_service(service_address: str, timeout: float) -> Optional[Response]:
    async with httpx.AsyncClient() as client:
        response = await client.get(service_address, timeout=timeout)
        return response


async def ping_services(return_msg: bool = False) -> Optional[List[str]]:
    messages = []

    for name, service in app.g_services.items():
        start = time.time()
        service_address = (
            f"http://{service['address']}:{service['port']}{service['health_endpoint']}"
        )

        try:
            response = await ping_service(service_address, timeout=1.0)
            response_time = (time.time() - start) * 1000

            app.g_services[name]["last_check"] = datetime.timestamp(datetime.now())

            if response.status_code == 200:
                app.g_services[name]["response_time"] = response_time
            else:
                app.g_services[name]["status"] = "down"

            logger.info(
                f"Pinging {service_address}, {app.g_services[name]['status']}, response={app.g_services[name]['response_time']}"
            )

            messages.append(
                f"Pinging {service_address}, {app.g_services[name]['status']}, response={app.g_services[name]['response_time']}"
            )
        except Exception as e:
            app.g_services[name]["status"] = "down"
            app.g_services[name]["response_time"] = 0
            logger.error(f"Pinging service {name} failed. Error: {str(e)}")

            messages.append(f"Pinging service {name} failed. Error: {str(e)}")

    return messages


async def schedule_services_pinging():
    """Schedule service pinging"""
    poll_duration_in_minute = 5

    scheduler.add_job(
        ping_services,
        IntervalTrigger(minutes=poll_duration_in_minute),
        id="services_ping",
        replace_existing=True,
    )
    logger.info(
        f"Scheduled pinging services status every {poll_duration_in_minute} minutes"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Registry Service...")

    # load services
    app.g_services = load_services()

    # Start scheduler for service pinging
    scheduler.start()
    await schedule_services_pinging()
    logger.info("Scheduler started")

    yield

    # save services
    save_services(app.g_services)

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


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_service(service_data: ServiceRegister):
    try:
        registered_time = datetime.timestamp(datetime.now())

        service = ServiceStatus(
            name=service_data.name,
            port=service_data.port,
            address=service_data.address,
            last_check=registered_time,
            response_time=0,
            status="healthy",
            health_endpoint=service_data.health_endpoint,
        )

        # ping back the register service
        start = time.time()
        service_address = (
            f"http://{service.address}:{service.port}{service.health_endpoint}"
        )
        logger.info(f"pingiiing {service_address}")
        response = await ping_service(service_address, 1.0)
        response_time = (time.time() - start) * 1000

        if response.status_code == status.HTTP_200_OK:
            service.response_time = response_time

        app.g_services[service_data.name] = dict(service)

        # save services
        save_services(app.g_services)
    except Exception as e:
        logger.error(f"{str(e)}")

    return app.g_services[service_data.name]


@app.get("/services", status_code=status.HTTP_200_OK)
async def get_services():
    return app.g_services


@app.get("/services/<service_id:str>")
async def get_service(service_id: Dict):
    return app.g_services


@app.get("/reset")
async def reset():
    app.g_services = reset_services()

    return {"message": "resetted"}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "service-registry-api"}


@app.get("/ping")
async def do_ping():
    messages = await ping_services(True)
    return {"message": "done pinging", "ping_logs": messages}
