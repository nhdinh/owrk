"""
API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import assets, categories, attachments

api_router = APIRouter()

# Include endpoint routers
# Note: categories is now included as a sub-router of assets to ensure proper route ordering
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(attachments.router, prefix="/assets", tags=["attachments"])
