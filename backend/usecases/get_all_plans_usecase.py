"""
Use case for getting all plans with optional pagination
"""
from typing import List, Optional
from fastapi import Depends

from repositories.plan_repository import PlanRepository
from models.domain import Plan

class GetAllPlansUseCaseHelper:
    """Helper class to manage dependencies and execute use case logic"""
    
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository
    
    async def execute(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Plan]:
        """Get all plans with optional pagination"""
        try:
            # Get plans from repository with pagination
            plan_documents = await self.plan_repository.get_all(limit=limit, offset=offset)
            
            # Convert documents to domain objects
            plans = []
            for doc in plan_documents:
                try:
                    # Convert ObjectId to string if present
                    if "_id" in doc:
                        doc["id"] = str(doc["_id"])
                        del doc["_id"]
                    
                    # Create Plan domain object
                    plan = Plan(**doc)
                    plans.append(plan)
                except Exception as e:
                    print(f"Error converting plan document to domain object: {e}")
                    continue
            
            return plans
            
        except Exception as e:
            print(f"Error in GetAllPlansUseCase: {e}")
            raise

class GetAllPlansUseCase:
    """Use case for getting all plans"""
    
    def __init__(self, plan_repository: PlanRepository = Depends()):
        self.helper = GetAllPlansUseCaseHelper(plan_repository)
    
    async def execute(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Plan]:
        """Execute the get all plans use case"""
        return await self.helper.execute(limit, offset)