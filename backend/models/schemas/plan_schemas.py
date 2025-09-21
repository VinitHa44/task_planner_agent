"""
API Schemas for Plan-related endpoints
Handles request/response models for the API layer
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskSchema(BaseModel):
    """API schema for Task data"""
    id: Optional[str] = None
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: Optional[str] = None
    external_info: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DaySchema(BaseModel):
    """API schema for Day data"""
    day_number: int
    date: Optional[str] = None
    tasks: List[TaskSchema]
    summary: str
    weather_info: Optional[List[Dict[str, Any]]] = None

class PlanCreateRequest(BaseModel):
    """Request schema for creating a new plan"""
    goal: str
    description: Optional[str] = None

class PlanUpdateRequest(BaseModel):
    """Request schema for updating a plan"""
    goal: Optional[str] = None
    description: Optional[str] = None
    days: Optional[List[DaySchema]] = None
    status: Optional[str] = None

class PlanResponse(BaseModel):
    """Response schema for Plan data"""
    id: str
    goal: str
    description: str
    days: List[DaySchema]
    total_duration: str
    created_at: datetime
    updated_at: datetime
    status: str

class PlanListResponse(BaseModel):
    """Response schema for list of plans"""
    plans: List[PlanResponse]
    total: int

class HealthCheckResponse(BaseModel):
    """Response schema for health check"""
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)