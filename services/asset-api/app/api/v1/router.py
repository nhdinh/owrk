"""
API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import assets, categories, attachments

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(attachments.router, prefix="/assets", tags=["attachments"])
