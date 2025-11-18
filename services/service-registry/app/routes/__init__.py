"""
API Routes for Service Registry
"""

from .monitoring import router as monitoring_router

__all__ = ["monitoring_router"]
