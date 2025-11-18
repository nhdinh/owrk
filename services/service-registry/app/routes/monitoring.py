"""
Monitoring and Analytics API Endpoints
Advanced monitoring dashboard with historical metrics and analytics
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import redis

from app.core.config import settings
from app.storage import RedisServiceStore, InfluxServiceStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Analytics"])

# Initialize storage clients
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


# Response Models
class ServiceUptimeResponse(BaseModel):
    service_name: str
    uptime_percent: Optional[float]
    period_hours: int


class ResponseTimePercentilesResponse(BaseModel):
    service_name: str
    p50: Optional[float]
    p95: Optional[float]
    p99: Optional[float]
    period_hours: int


class ServiceMetricsSummaryResponse(BaseModel):
    service_name: str
    period_hours: int
    uptime_percent: Optional[float]
    average_response_time: Optional[float]
    response_time_percentiles: Optional[dict]
    downtime_events_count: int
    downtime_events: list


class AllServicesUptimeResponse(BaseModel):
    services: list
    period_hours: int


# Endpoints

@router.get("/uptime/{service_name}", response_model=ServiceUptimeResponse)
async def get_service_uptime(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720, description="Number of hours to look back (1-720)")
):
    """
    Get service uptime percentage for the specified time period

    Args:
        service_name: Name of the service
        hours: Number of hours to analyze (default: 24, max: 720/30 days)

    Returns:
        Service uptime percentage and period
    """
    try:
        uptime = influx_store.get_service_uptime(service_name, hours)

        if uptime is None:
            logger.warning(f"No uptime data found for {service_name}")

        return {
            "service_name": service_name,
            "uptime_percent": uptime,
            "period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error getting uptime for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get uptime: {str(e)}")


@router.get("/uptime", response_model=AllServicesUptimeResponse)
async def get_all_services_uptime(
    hours: int = Query(default=24, ge=1, le=720, description="Number of hours to look back")
):
    """
    Get uptime for all services

    Args:
        hours: Number of hours to analyze (default: 24)

    Returns:
        List of all services with their uptime percentages
    """
    try:
        uptime_data = influx_store.get_all_services_uptime(hours)

        return {
            "services": uptime_data,
            "period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error getting all services uptime: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get uptime: {str(e)}")


@router.get("/response-time/{service_name}")
async def get_average_response_time(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720)
):
    """
    Get average response time for a service

    Args:
        service_name: Name of the service
        hours: Number of hours to analyze

    Returns:
        Average response time in milliseconds
    """
    try:
        avg_time = influx_store.get_average_response_time(service_name, hours)

        return {
            "service_name": service_name,
            "average_response_time_ms": avg_time,
            "period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error getting avg response time for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/percentiles/{service_name}", response_model=ResponseTimePercentilesResponse)
async def get_response_time_percentiles(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720)
):
    """
    Get response time percentiles (p50, p95, p99) for a service

    This helps identify outliers and tail latencies

    Args:
        service_name: Name of the service
        hours: Number of hours to analyze

    Returns:
        Response time percentiles in milliseconds
    """
    try:
        percentiles = influx_store.get_response_time_percentiles(service_name, hours)

        if not percentiles:
            percentiles = {"p50": None, "p95": None, "p99": None}

        return {
            "service_name": service_name,
            "p50": percentiles.get("p50"),
            "p95": percentiles.get("p95"),
            "p99": percentiles.get("p99"),
            "period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error getting percentiles for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/downtime/{service_name}")
async def get_downtime_events(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720)
):
    """
    Get downtime events for a service

    Args:
        service_name: Name of the service
        hours: Number of hours to look back

    Returns:
        List of downtime events with timestamps
    """
    try:
        events = influx_store.get_downtime_events(service_name, hours)

        return {
            "service_name": service_name,
            "downtime_events": events,
            "total_events": len(events),
            "period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error getting downtime events for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{service_name}")
async def get_service_history(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720),
    interval: str = Query(default="5m", description="Aggregation interval (e.g., 5m, 1h, 1d)")
):
    """
    Get historical service metrics with aggregation

    Args:
        service_name: Name of the service
        hours: Number of hours to look back
        interval: Aggregation interval (5m, 15m, 1h, 6h, 1d)

    Returns:
        Time-series data points
    """
    try:
        history = influx_store.get_service_history(service_name, hours, interval)

        return {
            "service_name": service_name,
            "period_hours": hours,
            "interval": interval,
            "data_points": len(history),
            "history": history
        }

    except Exception as e:
        logger.error(f"Error getting history for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{service_name}", response_model=ServiceMetricsSummaryResponse)
async def get_service_metrics_summary(
    service_name: str,
    hours: int = Query(default=24, ge=1, le=720)
):
    """
    Get comprehensive metrics summary for a service

    Includes:
    - Uptime percentage
    - Average response time
    - Response time percentiles (p50, p95, p99)
    - Downtime events

    Args:
        service_name: Name of the service
        hours: Number of hours to analyze

    Returns:
        Comprehensive service metrics
    """
    try:
        summary = influx_store.get_service_metrics_summary(service_name, hours)

        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for {service_name}"
            )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics summary for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_data(
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours for dashboard data")
):
    """
    Get comprehensive dashboard data for all services

    Provides a complete overview for the monitoring dashboard

    Args:
        hours: Number of hours to analyze (max 7 days for dashboard)

    Returns:
        Dashboard data with all services metrics
    """
    try:
        redis_store = RedisServiceStore(redis_client)

        # Get current service statuses from Redis
        services = redis_store.get_all()

        # Get historical uptime for all services
        uptime_data = influx_store.get_all_services_uptime(hours)
        uptime_map = {item["service_name"]: item["uptime_percent"] for item in uptime_data}

        # Build dashboard data
        dashboard_services = []
        for name, service in services.items():
            dashboard_services.append({
                "name": name,
                "status": service.get("status"),
                "current_response_time": service.get("response_time"),
                "address": service.get("address"),
                "port": service.get("port"),
                "uptime_percent": uptime_map.get(name),
                "last_check": service.get("last_check")
            })

        # Get overall statistics
        stats = redis_store.get_statistics()

        return {
            "period_hours": hours,
            "statistics": stats,
            "services": dashboard_services,
            "total_services": len(dashboard_services),
            "timestamp": stats.get("timestamp")
        }

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-history/{service_name}")
async def get_recent_history_from_redis(
    service_name: str,
    limit: int = Query(default=20, ge=1, le=100, description="Number of recent items")
):
    """
    Get recent history from Redis (last N health checks)

    This provides quick access to recent data without querying InfluxDB

    Args:
        service_name: Name of the service
        limit: Number of recent items to retrieve

    Returns:
        Recent history entries from Redis
    """
    try:
        redis_store = RedisServiceStore(redis_client)
        history = redis_store.get_history(service_name, limit)

        return {
            "service_name": service_name,
            "recent_history": history,
            "count": len(history)
        }

    except Exception as e:
        logger.error(f"Error getting recent history for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
