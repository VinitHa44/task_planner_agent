"""
Health router - defines API endpoints for health checks
"""
from fastapi import APIRouter, Depends

from models.schemas import HealthCheckResponse
from controllers import HealthController
from utils.error_handler import handle_exceptions

# Create router instance
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
@handle_exceptions
async def health_check(
    health_controller: HealthController = Depends(HealthController)
):
    """Basic health check endpoint"""
    return await health_controller.health_check()


@router.get("/health/detailed")
@handle_exceptions
async def detailed_health_check(
    health_controller: HealthController = Depends(HealthController)
):
    """Detailed health check with component status"""
    return await health_controller.detailed_health_check()