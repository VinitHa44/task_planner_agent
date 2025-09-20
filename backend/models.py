from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: Optional[str] = None
    external_info: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Day(BaseModel):
    day_number: int
    date: Optional[str] = None
    tasks: List[Task]
    summary: str
    weather_info: Optional[List[Dict[str, Any]]] = None

class Plan(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    goal: str
    description: str
    days: List[Day]
    total_duration: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"

class PlanCreate(BaseModel):
    goal: str
    description: Optional[str] = None

class PlanResponse(BaseModel):
    id: str
    goal: str
    description: str
    days: List[Day]
    total_duration: str
    created_at: datetime
    status: str
