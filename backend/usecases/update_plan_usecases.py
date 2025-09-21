"""
Plan update and delete use cases
"""
from typing import Optional
from datetime import datetime
from fastapi import Depends

from models.domain import Plan
from repositories import PlanRepository

class UpdatePlanUseCase:
    """Use case for updating existing plans"""
    
    def __init__(self, plan_repository: PlanRepository = Depends(PlanRepository)):
        self.plan_repository = plan_repository
    
    async def execute(self, plan_id: str, plan: Plan) -> Optional[Plan]:
        """Update a plan and return the updated plan"""
        # Update the updated_at timestamp
        plan.updated_at = datetime.utcnow()
        
        # Convert to dict and remove id for update
        plan_dict = plan.dict()
        plan_dict.pop("id", None)
        
        # Perform the update
        success = await self.plan_repository.update(plan_id, plan_dict)
        
        if success:
            # Return the updated plan
            updated_plan_data = await self.plan_repository.get_by_id(plan_id)
            if updated_plan_data:
                return Plan(**updated_plan_data)
        
        return None

class DeletePlanUseCase:
    """Use case for deleting plans"""
    
    def __init__(self, plan_repository: PlanRepository = Depends(PlanRepository)):
        self.plan_repository = plan_repository
    
    async def execute(self, plan_id: str) -> bool:
        """Delete a plan by ID"""
        return await self.plan_repository.delete(plan_id)

class UpdatePlanStatusUseCase:
    """Use case for updating only the status of a plan"""
    
    def __init__(self, plan_repository: PlanRepository = Depends(PlanRepository)):
        self.plan_repository = plan_repository
    
    async def execute(self, plan_id: str, new_status: str) -> Optional[Plan]:
        """Update only the status of a plan"""
        # Get the current plan
        plan_data = await self.plan_repository.get_by_id(plan_id)
        if not plan_data:
            return None
        
        # Update the status and timestamp
        plan_data["status"] = new_status
        plan_data["updated_at"] = datetime.utcnow()
        
        # Remove id for update
        plan_data.pop("id", None)
        
        # Perform the update
        success = await self.plan_repository.update(plan_id, plan_data)
        
        if success:
            # Return the updated plan
            updated_plan_data = await self.plan_repository.get_by_id(plan_id)
            if updated_plan_data:
                return Plan(**updated_plan_data)
        
        return None