"""
Main API Router for Auth Service
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, permissions, users_cqrs

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(permissions.router)

# NEW: CQRS endpoints (demo)
api_router.include_router(users_cqrs.router, tags=["CQRS Demo"])


# Status endpoint
@api_router.get("/status")
async def status():
    """
    Status endpoint to verify service is running
    """
    return {
        "service": "Auth Service",
        "status": "running",
        "message": "Authentication endpoints are now available",
    }
