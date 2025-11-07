"""
API v1 Router
Aggregates all v1 API endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import vendors, purchase_requests, quotations

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(vendors.router)
api_router.include_router(purchase_requests.router)
api_router.include_router(quotations.router)

# Future routers will be added here:
# api_router.include_router(framework_contracts.router)
# api_router.include_router(purchase_orders.router)
