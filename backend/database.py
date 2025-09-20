from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from models import Plan, PlanCreate
import os
from bson import ObjectId

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
        self.db = self.client[os.getenv("DATABASE_NAME", "task_planning_db")]
        self.plans = self.db.plans
    
    async def create_plan(self, plan: Plan) -> str:
        """Create a new plan in the database"""
        plan_dict = plan.dict()
        
        # Remove any existing id field before insertion
        plan_dict.pop('id', None)
        
        # Let MongoDB generate the _id automatically
        result = await self.plans.insert_one(plan_dict)
        return str(result.inserted_id)
    
    async def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID"""
        try:
            # Try to convert to ObjectId if it's a valid ObjectId string
            try:
                query_id = ObjectId(plan_id)
            except:
                query_id = plan_id
                
            plan_data = await self.plans.find_one({"_id": query_id})
            if plan_data:
                # Handle both ObjectId and string _id formats
                plan_data["id"] = str(plan_data.pop("_id"))
                
                # Clean up the data structure
                plan_data = self._clean_plan_data(plan_data)
                
                return Plan(**plan_data)
        except Exception as e:
            print(f"Error in get_plan: {e}")
        return None
    
    def _clean_plan_data(self, plan_data):
        """Clean up plan data to match our Pydantic models"""
        from bson import ObjectId
        
        # Ensure id is always a valid string - convert from _id
        if "_id" in plan_data:
            plan_data["id"] = str(plan_data["_id"])
            plan_data.pop("_id", None)  # Remove _id after converting
        elif "id" not in plan_data or plan_data.get("id") is None:
            plan_data["id"] = str(ObjectId())
        
        # Clean up days and tasks
        if "days" in plan_data:
            for day in plan_data["days"]:
                if "tasks" in day:
                    for task in day["tasks"]:
                        # Ensure task has a valid ID
                        if "id" not in task or task["id"] is None:
                            task["id"] = str(ObjectId())
                        
                        # Remove extra fields that might cause issues
                        task.pop("created_at", None)
                        task.pop("external_info", None)
                        
                        # Ensure required fields exist
                        if "description" not in task or not task["description"]:
                            task["description"] = task.get("title", "No description")
                        
                        # Ensure status is valid
                        if "status" not in task:
                            task["status"] = "pending"
        
        return plan_data
    
    async def get_all_plans(self) -> List[Plan]:
        """Get all plans"""
        plans = []
        try:
            async for plan_data in self.plans.find().sort("created_at", -1):
                # Clean up the data structure
                plan_data = self._clean_plan_data(plan_data)
                
                # Create Plan object with error handling
                try:
                    plans.append(Plan(**plan_data))
                except Exception as e:
                    print(f"Error creating Plan object: {e}")
                    print(f"Plan data keys: {list(plan_data.keys())}")
                    # Try to salvage what we can
                    try:
                        # Create a minimal valid plan
                        minimal_plan = {
                            "id": plan_data.get("id", str(ObjectId())),
                            "goal": plan_data.get("goal", "Unknown goal"),
                            "description": plan_data.get("description", "No description"),
                            "days": [],
                            "total_duration": plan_data.get("total_duration", "Unknown"),
                            "created_at": plan_data.get("created_at"),
                            "updated_at": plan_data.get("updated_at"),
                            "status": plan_data.get("status", "active")
                        }
                        plans.append(Plan(**minimal_plan))
                    except Exception as e2:
                        print(f"Could not salvage plan: {e2}, skipping...")
                        continue
                    
        except Exception as e:
            print(f"Error in get_all_plans: {e}")
            
        return plans
    
    async def update_plan(self, plan_id: str, plan: Plan) -> bool:
        """Update a plan"""
        plan_dict = plan.dict()
        plan_dict.pop("id", None)
        result = await self.plans.update_one(
            {"_id": plan_id},
            {"$set": plan_dict}
        )
        return result.modified_count > 0
    
    async def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        result = await self.plans.delete_one({"_id": plan_id})
        return result.deleted_count > 0
    
    async def close(self):
        """Close database connection"""
        self.client.close()