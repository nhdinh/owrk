"""
Main API Router for Dashboard Service
"""

from fastapi import APIRouter
from app.api.v1.endpoints import dashboard

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(dashboard.router)


# Status endpoint
@api_router.get("/status")
async def status():
    """
    Status endpoint to verify service is running
    """
    return {
        "service": "Dashboard Service",
        "status": "running",
        "message": "Dashboard endpoints are available",
    }
