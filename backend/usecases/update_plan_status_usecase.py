"""
Use case for updating only the status of a plan
"""
from typing import Optional
from fastapi import Depends

from repositories.plan_repository import PlanRepository
from models.domain import Plan

class UpdatePlanStatusUseCaseHelper:
    """Helper class to manage dependencies and execute use case logic"""
    
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository
    
    async def execute(self, plan_id: str, new_status: str) -> Optional[Plan]:
        """Update only the status of a plan"""
        try:
            # Get the current plan
            plan_doc = await self.plan_repository.get_by_id(plan_id)
            if not plan_doc:
                return None
            
            # Convert ObjectId to string if present
            if "_id" in plan_doc:
                plan_doc["id"] = str(plan_doc["_id"])
                del plan_doc["_id"]
            
            # Create Plan domain object
            plan = Plan(**plan_doc)
            
            # Update only the status
            plan.status = new_status
            
            # Convert back to document format for update
            update_doc = plan.dict()
            if "id" in update_doc:
                del update_doc["id"]  # Remove ID from update document
            
            # Update in repository
            success = await self.plan_repository.update(plan_id, update_doc)
            if not success:
                return None
            
            # Return the updated plan
            return plan
            
        except Exception as e:
            print(f"Error in UpdatePlanStatusUseCase: {e}")
            raise

class UpdatePlanStatusUseCase:
    """Use case for updating plan status"""
    
    def __init__(self, plan_repository: PlanRepository = Depends()):
        self.helper = UpdatePlanStatusUseCaseHelper(plan_repository)
    
    async def execute(self, plan_id: str, new_status: str) -> Optional[Plan]:
        """Execute the update plan status use case"""
        return await self.helper.execute(plan_id, new_status)