# pyright: reportAttributeAccessIssue=false

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import time
from typing import List, Optional
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import HealthCheckMethods, settings
from .schema import *
from .data import load_services, save_services, reset_services
from .helper import get_host_address, do_one_ping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


async def ping_service(service_name: str, timeout: float) -> Optional[float]:
    service_addr = app.g_services[service_name]["address"]

    t = do_one_ping(service_addr, timeout)

    return t * 1000


async def check_health(service_name: str, timeout: float) -> Optional[float]:
    hostname = app.g_services[service_name]["hostname"]
    service_port = app.g_services[service_name]["port"]
    health_endpoint = app.g_services[service_name]["health_endpoint"]

    start_time = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://{hostname}:{service_port}{health_endpoint}", timeout=timeout
        )

        if response.status_code == status.HTTP_200_OK:
            response_time = (time.time() - start_time) * 1000

            return response_time

    return None


async def ping_services(return_msg: bool = False) -> Optional[List[str]]:
    messages = []

    for name in app.g_services.keys():
        try:
            response_time: Optional[float] = None

            if settings.SERVICE_HEALTH_CHECK == HealthCheckMethods.PING:
                response_time = await ping_service(name, timeout=0.5)
            elif settings.SERVICE_HEALTH_CHECK == HealthCheckMethods.HTTPX:
                response_time = await check_health(name, timeout=0.5)

            if response_time is not None:
                app.g_services[name]["response_time"] = response_time
            else:
                app.g_services[name]["status"] = "down"

            logger.info(
                f"Pinging {name}, {app.g_services[name]['status']}, response={app.g_services[name]['response_time']}"
            )

            messages.append(
                f"Pinging {name}, {app.g_services[name]['status']}, response={app.g_services[name]['response_time']}"
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
        host_addr = get_host_address(service_data.hostname)
        logger.info(f"Registered service {service_data.name} - IP: {host_addr}")

        service = ServiceStatus(
            name=service_data.name,
            port=service_data.port,
            hostname=service_data.hostname,
            address=host_addr,
            last_check=registered_time,
            response_time=0,
            status="healthy",
            health_endpoint=service_data.health_endpoint,
        )

        app.g_services[service_data.name] = dict(service)

        # save services
        save_services(app.g_services)

        return app.g_services[service_data.name]
    except Exception as e:
        logger.error(f"{str(e)}")


@app.get("/services", status_code=status.HTTP_200_OK)
async def get_services():
    return app.g_services


@app.get("/services/<service_id:str>", status_code=status.HTTP_200_OK)
async def get_service(service_id: str):
    if service_id in app.g_services.keys():
        return app.g_services[service_id]

    return None


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
