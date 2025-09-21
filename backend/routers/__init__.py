"""
Export all routers for easy importing
"""
from .plan_router import router as plan_router
from .health_router import router as health_router

__all__ = [
    "plan_router",
    "health_router"
]