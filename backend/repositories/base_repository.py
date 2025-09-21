"""
Base repository interface and common database operations
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class BaseRepository(ABC):
    """Base repository interface for common database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    @abstractmethod
    async def create(self, entity: Dict[str, Any]) -> str:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all entities with optional pagination"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, entity: Dict[str, Any]) -> bool:
        """Update an entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total entities"""
        pass