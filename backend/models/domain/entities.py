"""
Domain entities representing core business objects
These are the core business models independent of API or database concerns
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(BaseModel):
    """Core Task domain entity"""
    id: Optional[str] = None
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: Optional[str] = None
    external_info: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class Day(BaseModel):
    """Core Day domain entity"""
    day_number: int
    date: Optional[str] = None
    tasks: List[Task]
    summary: str
    weather_info: Optional[List[Dict[str, Any]]] = None

class Plan(BaseModel):
    """Core Plan domain entity"""
    id: Optional[str] = None
    goal: str
    description: str
    days: List[Day]
    total_duration: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"

class GoalInfo(BaseModel):
    """Extracted information from a user's goal"""
    destination: str = ""
    duration: int = 3
    activities: List[str] = []
    preferences: List[str] = []
    budget_considerations: str = ""
    time_of_year: str = ""
    timing_keywords: Optional[str] = None

class ExternalInfo(BaseModel):
    """External information gathered for plan enhancement"""
    trip_start_date: Optional[datetime] = None
    trip_end_date: Optional[datetime] = None
    trip_duration: int = 1
    weather: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None