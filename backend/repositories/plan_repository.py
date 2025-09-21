"""
Plan repository for database operations related to plans
"""
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

from .base_repository import BaseRepository
from models.database import PlanDocument
from models.domain import Plan
from config.database import db_manager

class PlanRepository(BaseRepository):
    """Repository for Plan database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase = Depends(lambda: db_manager.get_database())):
        super().__init__(db)
        self.collection = db.plans
    
    async def create(self, plan_data: Dict[str, Any]) -> str:
        """Create a new plan in the database"""
        try:
            # Convert to document format
            doc = PlanDocument.to_document(plan_data)
            
            # Insert into database
            result = await self.collection.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating plan: {e}")
            raise
    
    async def get_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a plan by ID"""
        try:
            # Try to convert to ObjectId if it's a valid ObjectId string
            try:
                query_id = ObjectId(plan_id)
            except:
                query_id = plan_id
            
            # Find the document
            doc = await self.collection.find_one({"_id": query_id})
            if doc:
                return PlanDocument.from_document(doc)
            return None
        except Exception as e:
            print(f"Error getting plan by ID {plan_id}: {e}")
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all plans with optional pagination"""
        try:
            cursor = self.collection.find().sort("created_at", -1)
            
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
            
            plans = []
            async for doc in cursor:
                try:
                    plan_data = PlanDocument.from_document(doc)
                    plans.append(plan_data)
                except Exception as e:
                    print(f"Error processing plan document: {e}")
                    # Try to create a minimal valid plan
                    try:
                        minimal_plan = {
                            "id": str(doc.get("_id", ObjectId())),
                            "goal": doc.get("goal", "Unknown goal"),
                            "description": doc.get("description", "No description"),
                            "days": [],
                            "total_duration": doc.get("total_duration", "Unknown"),
                            "created_at": doc.get("created_at"),
                            "updated_at": doc.get("updated_at"),
                            "status": doc.get("status", "active")
                        }
                        plans.append(minimal_plan)
                    except Exception as e2:
                        print(f"Could not salvage plan: {e2}, skipping...")
                        continue
            
            return plans
        except Exception as e:
            print(f"Error getting all plans: {e}")
            return []
    
    async def update(self, plan_id: str, plan_data: Dict[str, Any]) -> bool:
        """Update a plan"""
        try:
            # Try to convert to ObjectId if it's a valid ObjectId string
            try:
                query_id = ObjectId(plan_id)
            except:
                query_id = plan_id
            
            # Convert to document format and remove id
            doc = PlanDocument.to_document(plan_data)
            doc.pop("id", None)
            
            # Update the document
            result = await self.collection.update_one(
                {"_id": query_id},
                {"$set": doc}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating plan {plan_id}: {e}")
            return False
    
    async def delete(self, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            # Try to convert to ObjectId if it's a valid ObjectId string
            try:
                query_id = ObjectId(plan_id)
            except:
                query_id = plan_id
            
            result = await self.collection.delete_one({"_id": query_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting plan {plan_id}: {e}")
            return False
    
    async def count(self) -> int:
        """Count total plans"""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting plans: {e}")
            return 0
    
    async def search_by_goal(self, goal_pattern: str) -> List[Dict[str, Any]]:
        """Search plans by goal pattern (alias for find_by_goal)"""
        return await self.find_by_goal(goal_pattern)
    
    async def find_by_goal(self, goal_pattern: str) -> List[Dict[str, Any]]:
        """Find plans by goal pattern"""
        try:
            cursor = self.collection.find({
                "goal": {"$regex": goal_pattern, "$options": "i"}
            }).sort("created_at", -1)
            
            plans = []
            async for doc in cursor:
                plan_data = PlanDocument.from_document(doc)
                plans.append(plan_data)
            
            return plans
        except Exception as e:
            print(f"Error finding plans by goal: {e}")
            return []
    
    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find plans by status"""
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", -1)
            
            plans = []
            async for doc in cursor:
                plan_data = PlanDocument.from_document(doc)
                plans.append(plan_data)
            
            return plans
        except Exception as e:
            print(f"Error finding plans by status: {e}")
            return []