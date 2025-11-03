"""
Dashboard schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SystemStats(BaseModel):
    """Overall system statistics"""

    total_users: int
    active_users: int
    inactive_users: int
    total_roles: int
    users_with_mfa: int


class AssetStats(BaseModel):
    """Asset statistics"""

    total_assets: int
    available_assets: int
    assigned_assets: int
    in_maintenance_assets: int
    disposed_assets: int


class ActivityLog(BaseModel):
    """Recent activity log entry"""

    id: int
    timestamp: datetime
    user_email: str
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[str] = None


class DashboardOverview(BaseModel):
    """Complete dashboard overview"""

    system_stats: SystemStats
    asset_stats: AssetStats
    recent_activity: List[ActivityLog]


class SystemHealth(BaseModel):
    """System health status"""

    service: str
    status: str  # "healthy", "degraded", "down"
    response_time_ms: Optional[float] = None
    last_check: datetime


class DashboardHealth(BaseModel):
    """Dashboard health check"""

    services: List[SystemHealth]
    overall_status: str  # "healthy", "degraded", "down"
