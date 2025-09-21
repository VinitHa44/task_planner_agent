"""
Use case for searching plans by various criteria
"""
from typing import List
from fastapi import Depends

from repositories.plan_repository import PlanRepository
from models.domain import Plan

class SearchPlansUseCaseHelper:
    """Helper class to manage dependencies and execute use case logic"""
    
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository
    
    async def search_by_goal(self, goal_pattern: str) -> List[Plan]:
        """Search plans by goal pattern"""
        try:
            # Search for plans matching the goal pattern
            plan_documents = await self.plan_repository.search_by_goal(goal_pattern)
            
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
            print(f"Error in SearchPlansUseCase.search_by_goal: {e}")
            raise

class SearchPlansUseCase:
    """Use case for searching plans"""
    
    def __init__(self, plan_repository: PlanRepository = Depends()):
        self.helper = SearchPlansUseCaseHelper(plan_repository)
    
    async def search_by_goal(self, goal_pattern: str) -> List[Plan]:
        """Execute the search plans by goal use case"""
        return await self.helper.search_by_goal(goal_pattern)