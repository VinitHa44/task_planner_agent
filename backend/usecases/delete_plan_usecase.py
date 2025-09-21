"""
Use case for deleting a plan
"""
from fastapi import Depends

from repositories.plan_repository import PlanRepository

class DeletePlanUseCaseHelper:
    """Helper class to manage dependencies and execute use case logic"""
    
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository
    
    async def execute(self, plan_id: str) -> bool:
        """Delete a plan by ID"""
        try:
            # Delete the plan from repository
            success = await self.plan_repository.delete(plan_id)
            return success
            
        except Exception as e:
            print(f"Error in DeletePlanUseCase: {e}")
            raise

class DeletePlanUseCase:
    """Use case for deleting a plan"""
    
    def __init__(self, plan_repository: PlanRepository = Depends()):
        self.helper = DeletePlanUseCaseHelper(plan_repository)
    
    async def execute(self, plan_id: str) -> bool:
        """Execute the delete plan use case"""
        return await self.helper.execute(plan_id)