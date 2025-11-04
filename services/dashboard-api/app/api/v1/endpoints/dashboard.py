"""
Dashboard endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.dashboard import (
    SystemStats,
    AssetStats,
    DashboardOverview,
    ActivityLog,
    SystemHealth,
    DashboardHealth,
)
from datetime import datetime
from typing import List
import httpx
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get system statistics (users, roles, MFA)
    """
    try:
        # Query from auth_db.users table
        total_users = db.execute(text("SELECT COUNT(*) FROM auth_db.users")).scalar()

        active_users = db.execute(
            text("SELECT COUNT(*) FROM auth_db.users WHERE is_active = 1")
        ).scalar()

        inactive_users = total_users - active_users

        total_roles = db.execute(text("SELECT COUNT(*) FROM auth_db.roles")).scalar()

        users_with_mfa = db.execute(
            text("SELECT COUNT(*) FROM auth_db.users WHERE mfa_enabled = 1")
        ).scalar()

        return SystemStats(
            total_users=total_users or 0,
            active_users=active_users or 0,
            inactive_users=inactive_users or 0,
            total_roles=total_roles or 0,
            users_with_mfa=users_with_mfa or 0,
        )
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching system stats: {str(e)}"
        )


@router.get("/stats/assets", response_model=AssetStats)
async def get_asset_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get asset statistics
    """
    try:
        # Query from asset_db.assets table
        total_assets = db.execute(
            text("SELECT COUNT(*) FROM asset_db.assets WHERE deleted_at IS NULL")
        ).scalar()

        available_assets = db.execute(
            text(
                "SELECT COUNT(*) FROM asset_db.assets WHERE status = 'available' AND deleted_at IS NULL"
            )
        ).scalar()

        assigned_assets = db.execute(
            text(
                "SELECT COUNT(*) FROM asset_db.assets WHERE status = 'assigned' AND deleted_at IS NULL"
            )
        ).scalar()

        in_maintenance_assets = db.execute(
            text(
                "SELECT COUNT(*) FROM asset_db.assets WHERE status = 'in_maintenance' AND deleted_at IS NULL"
            )
        ).scalar()

        disposed_assets = db.execute(
            text(
                "SELECT COUNT(*) FROM asset_db.assets WHERE status = 'disposed' AND deleted_at IS NULL"
            )
        ).scalar()

        return AssetStats(
            total_assets=total_assets or 0,
            available_assets=available_assets or 0,
            assigned_assets=assigned_assets or 0,
            in_maintenance_assets=in_maintenance_assets or 0,
            disposed_assets=disposed_assets or 0,
        )
    except Exception as e:
        logger.error(f"Error fetching asset stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching asset stats: {str(e)}"
        )


@router.get("/activity", response_model=List[ActivityLog])
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get recent activity logs from both auth and asset services

    Note: This is a simplified version. In a real system, you'd have
    a dedicated activity_logs table that aggregates events from all services.
    """
    try:
        # For now, return empty list
        # TODO: Implement activity logging system
        return []
    except Exception as e:
        logger.error(f"Error fetching activity logs: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching activity logs: {str(e)}"
        )


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get complete dashboard overview with all stats
    """
    try:
        # Fetch system stats
        system_stats = await get_system_stats(db=db, current_user=current_user)

        # Try to fetch asset stats, but use defaults if table doesn't exist yet
        try:
            asset_stats = await get_asset_stats(db=db, current_user=current_user)
        except Exception as asset_error:
            logger.warning(
                f"Could not fetch asset stats (table may not exist yet): {asset_error}"
            )
            # Return empty/default asset stats
            asset_stats = AssetStats(
                total_assets=0,
                available_assets=0,
                assigned_assets=0,
                in_maintenance_assets=0,
                disposed_assets=0,
            )

        recent_activity = await get_recent_activity(
            limit=10, db=db, current_user=current_user
        )

        return DashboardOverview(
            system_stats=system_stats,
            asset_stats=asset_stats,
            recent_activity=recent_activity,
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching dashboard overview: {str(e)}"
        )


@router.get("/health", response_model=DashboardHealth)
async def get_system_health(
    current_user: dict = Depends(get_current_user),
):
    """
    Check health of all microservices
    """
    services = []

    # Check Auth API
    try:
        start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get("http://auth-api:8000/health", timeout=5.0)
            response_time = (time.time() - start) * 1000
            if response.status_code == 200:
                services.append(
                    SystemHealth(
                        service="auth-api",
                        status="healthy",
                        response_time_ms=response_time,
                        last_check=datetime.utcnow(),
                    )
                )
            else:
                services.append(
                    SystemHealth(
                        service="auth-api",
                        status="degraded",
                        response_time_ms=response_time,
                        last_check=datetime.utcnow(),
                    )
                )
    except Exception as e:
        logger.error(f"Auth API health check failed: {e}")
        services.append(
            SystemHealth(
                service="auth-api",
                status="down",
                last_check=datetime.utcnow(),
            )
        )

    # Check Asset API
    try:
        start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get("http://asset-api:8000/health", timeout=5.0)
            response_time = (time.time() - start) * 1000
            if response.status_code == 200:
                services.append(
                    SystemHealth(
                        service="asset-api",
                        status="healthy",
                        response_time_ms=response_time,
                        last_check=datetime.utcnow(),
                    )
                )
            else:
                services.append(
                    SystemHealth(
                        service="asset-api",
                        status="degraded",
                        response_time_ms=response_time,
                        last_check=datetime.utcnow(),
                    )
                )
    except Exception as e:
        logger.error(f"Asset API health check failed: {e}")
        services.append(
            SystemHealth(
                service="asset-api",
                status="down",
                last_check=datetime.utcnow(),
            )
        )

    # Determine overall status
    all_healthy = all(s.status == "healthy" for s in services)
    any_down = any(s.status == "down" for s in services)

    if all_healthy:
        overall_status = "healthy"
    elif any_down:
        overall_status = "down"
    else:
        overall_status = "degraded"

    return DashboardHealth(services=services, overall_status=overall_status)
