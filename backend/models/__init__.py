"""
Models package - Export all models for easy importing across layers
"""
# Domain models (business entities)
from .domain import (
    TaskStatus,
    Task,
    Day,
    Plan,
    GoalInfo,
    ExternalInfo
)

# API schemas (request/response models)
from .schemas import (
    TaskSchema,
    DaySchema,
    PlanCreateRequest,
    PlanUpdateRequest,
    PlanResponse,
    PlanListResponse,
    HealthCheckResponse
)

# Database models (document structures)
from .database import (
    PlanDocument,
    TaskDocument
)

__all__ = [
    # Domain models
    "TaskStatus",
    "Task",
    "Day",
    "Plan", 
    "GoalInfo",
    "ExternalInfo",
    
    # API schemas
    "TaskSchema",
    "DaySchema",
    "PlanCreateRequest",
    "PlanUpdateRequest",
    "PlanResponse",
    "PlanListResponse", 
    "HealthCheckResponse",
    
    # Database models
    "PlanDocument",
    "TaskDocument"
]