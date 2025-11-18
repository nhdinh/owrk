# pyright: reportAttributeAccessIssue=false

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import List, Optional
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import redis

from app.core.config import HealthCheckMethods, settings
from app.schema import *
from app.helper import get_host_address, do_one_ping
from app.storage import RedisServiceStore, InfluxServiceStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Initialize storage backends
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=False,
)

influx_store = InfluxServiceStore(
    url=settings.INFLUXDB_URL,
    token=settings.INFLUXDB_TOKEN,
    org=settings.INFLUXDB_ORG,
    bucket=settings.INFLUXDB_BUCKET,
)


async def ping_service(service_name: str, timeout: float) -> Optional[float]:
    """Ping a service using ICMP"""
    redis_store = RedisServiceStore(redis_client)
    service = redis_store.get(service_name)
    if not service:
        return None

    service_addr = service["address"]
    t = do_one_ping(service_addr, timeout)

    if t is not None:
        return t * 1000  # Convert to milliseconds

    return None


async def check_health(service_name: str, timeout: float) -> Optional[float]:
    """Check service health via HTTP endpoint"""
    redis_store = RedisServiceStore(redis_client)
    service = redis_store.get(service_name)
    if not service:
        return None

    hostname = service["hostname"]
    service_port = service["port"]
    health_endpoint = service["health_endpoint"]

    start_time = asyncio.get_event_loop().time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{hostname}:{service_port}{health_endpoint}", timeout=timeout
            )

            if response.status_code == status.HTTP_200_OK:
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                return response_time
    except Exception as e:
        logger.debug(f"Health check failed for {service_name}: {e}")
        return None

    return None


async def ping_services(return_msg: bool = False) -> Optional[List[str]]:
    """Ping all registered services and update their status"""
    messages = []
    redis_store = RedisServiceStore(redis_client)

    services = redis_store.get_all()

    for name, service in services.items():
        try:
            response_time: Optional[float] = None

            if settings.SERVICE_HEALTH_CHECK == HealthCheckMethods.PING:
                response_time = await ping_service(name, timeout=0.5)
            elif settings.SERVICE_HEALTH_CHECK == HealthCheckMethods.HTTPX:
                response_time = await check_health(name, timeout=0.5)

            if response_time is not None:
                response_time = round(response_time, 1)
                new_status = "healthy"
            else:
                response_time = 0
                new_status = "down"

            # Update status in Redis
            redis_store.update_status(name, new_status, response_time)

            # Write metric to InfluxDB
            influx_store.write_service_metric(
                service_name=name,
                status=new_status,
                response_time=response_time,
                address=service["address"],
                port=service["port"],
            )

            messages.append(
                f"Pinging {name}, {new_status}, response={response_time}ms"
            )

        except Exception as e:
            logger.error(f"Pinging service {name} failed. Error: {str(e)}")
            # Mark as down in both stores
            redis_store.update_status(name, "down", 0)
            influx_store.write_service_metric(
                service_name=name,
                status="down",
                response_time=0,
                address=service.get("address", "unknown"),
                port=service.get("port", 0),
            )
            messages.append(f"Pinging service {name} failed. Error: {str(e)}")

    # Cleanup stale services
    stale_services = redis_store.cleanup_stale_services(max_age_seconds=600)
    if stale_services:
        logger.warning(f"⚠️  Marked {len(stale_services)} services as stale")

    if return_msg:
        return messages


async def schedule_services_pinging():
    """Schedule service pinging"""
    poll_duration_in_minute = 1  # Check every 1 minute

    scheduler.add_job(
        ping_services,
        IntervalTrigger(minutes=poll_duration_in_minute),
        id="services_ping",
        replace_existing=True,
    )

    logger.info(
        f"📅 Scheduled pinging services status every {poll_duration_in_minute} minute(s)"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("🚀 Starting Registry Service...")

    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise

    # Test InfluxDB connection
    try:
        influx_store.query_api.query(
            org=settings.INFLUXDB_ORG, query=f'buckets() |> filter(fn: (r) => r.name == "{settings.INFLUXDB_BUCKET}")'
        )
        logger.info("✅ InfluxDB connection successful")
    except Exception as e:
        logger.error(f"❌ InfluxDB connection failed: {e}")
        logger.warning("⚠️  Continuing without InfluxDB metrics storage")

    # Initialize Redis store (migrate existing data if needed)
    redis_store = RedisServiceStore(redis_client)
    logger.info(f"✅ Redis service store initialized ({redis_store.get_service_count()} services)")

    # Start scheduler for service pinging
    scheduler.start()
    await schedule_services_pinging()
    logger.info("✅ Scheduler started")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Registry Service...")
    scheduler.shutdown()
    influx_store.close()
    redis_client.close()
    logger.info("✅ Registry Service shutdown complete")


app = FastAPI(
    title="Service Registry API",
    description="Centralized service registry with real-time monitoring and historical metrics",
    version="2.0.0",
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
    redis_store = RedisServiceStore(redis_client)
    stats = redis_store.get_statistics()

    return {
        "service": "Service Registry",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "statistics": stats,
    }


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_service(service_data: ServiceRegister):
    """Register a new service"""
    try:
        redis_store = RedisServiceStore(redis_client)

        registered_time = datetime.timestamp(datetime.now())
        host_addr = get_host_address(service_data.hostname)
        logger.info(f"📝 Registering service {service_data.name} - IP: {host_addr}")

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

        # Save to Redis
        redis_store.register(dict(service))

        # Log registration event to InfluxDB
        influx_store.write_registration_event(
            service_name=service_data.name,
            hostname=service_data.hostname,
            address=host_addr,
            port=service_data.port,
        )

        logger.info(f"✅ Registered {service_data.name} successfully")

        return service

    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.get("/services", status_code=status.HTTP_200_OK)
async def get_services():
    """Get all registered services"""
    redis_store = RedisServiceStore(redis_client)
    return redis_store.get_all()


@app.get("/services/{service_name}", status_code=status.HTTP_200_OK)
async def get_service(service_name: str):
    """Get a specific service by name"""
    redis_store = RedisServiceStore(redis_client)
    service = redis_store.get(service_name)

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    return service


@app.delete("/services/{service_name}", status_code=status.HTTP_200_OK)
async def delete_service(service_name: str):
    """Deregister a service"""
    redis_store = RedisServiceStore(redis_client)
    service = redis_store.get(service_name)

    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    # Delete from Redis
    redis_store.delete(service_name)

    # Log deregistration event to InfluxDB
    influx_store.write_deregistration_event(service_name)

    logger.info(f"🗑️  Deregistered {service_name}")

    return {"message": f"Service {service_name} deregistered successfully"}


@app.get("/statistics", status_code=status.HTTP_200_OK)
async def get_statistics():
    """Get registry statistics"""
    redis_store = RedisServiceStore(redis_client)
    return redis_store.get_statistics()


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_store = RedisServiceStore(redis_client)

    return {
        "status": "healthy",
        "service": "service-registry",
        "total_services": redis_store.get_service_count(),
        "healthy_services": redis_store.get_healthy_count(),
    }


@app.get("/ping")
async def do_ping():
    """Manually trigger service health checks"""
    messages = await ping_services(True)
    return {"message": "done pinging", "ping_logs": messages}


@app.get("/reset")
async def reset():
    """Reset all service data (development only)"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403, detail="Reset is only allowed in development mode"
        )

    redis_store = RedisServiceStore(redis_client)
    services = redis_store.get_all()

    for service_name in services.keys():
        redis_store.delete(service_name)

    logger.warning("⚠️  All services reset")

    return {"message": "All services have been reset"}
