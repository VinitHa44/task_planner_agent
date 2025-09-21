"""
Health controller - handles application health and status checks
"""
from datetime import datetime
from models.schemas import HealthCheckResponse

class HealthController:
    """Controller for health check operations"""
    
    def __init__(self):
        pass
    
    async def health_check(self) -> HealthCheckResponse:
        """Return application health status"""
        return HealthCheckResponse(
            status="healthy",
            service="AI Task Planning Agent"
        )
    
    async def detailed_health_check(self) -> dict:
        """Return detailed health information"""
        return {
            "status": "healthy",
            "service": "AI Task Planning Agent",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "connected",
                "ai_service": "available",
                "weather_service": "available",
                "search_service": "available"
            }
        }