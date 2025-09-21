"""
Plan retrieval use cases - handle getting plans from the system
"""
from typing import List, Optional
from fastapi import Depends
from models.domain import Plan
from repositories import PlanRepository
from config.database import db_manager

class GetPlanUseCase:
    """Use case for retrieving a single plan by ID"""
    
    def __init__(self):
        self.plan_repository = PlanRepository(db_manager.get_database())
    
    async def execute(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID"""
        plan_data = await self.plan_repository.get_by_id(plan_id)
        if plan_data:
            return Plan(**plan_data)
        return None

class GetAllPlansUseCase:
    """Use case for retrieving all plans"""
    
    def __init__(self):
        self.plan_repository = PlanRepository(db_manager.get_database())
    
    async def execute(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Plan]:
        """Get all plans with optional pagination"""
        plans_data = await self.plan_repository.get_all(limit=limit, offset=offset)
        plans = []
        
        for plan_data in plans_data:
            try:
                plans.append(Plan(**plan_data))
            except Exception as e:
                print(f"Error creating Plan object from data: {e}")
                # Skip invalid plans
                continue
        
        return plans

class SearchPlansUseCase:
    """Use case for searching plans by various criteria"""
    
    def __init__(self):
        self.plan_repository = PlanRepository(db_manager.get_database())
    
    async def search_by_goal(self, goal_pattern: str) -> List[Plan]:
        """Search plans by goal pattern"""
        plans_data = await self.plan_repository.find_by_goal(goal_pattern)
        plans = []
        
        for plan_data in plans_data:
            try:
                plans.append(Plan(**plan_data))
            except Exception as e:
                print(f"Error creating Plan object from search data: {e}")
                continue
        
        return plans
    
    async def search_by_status(self, status: str) -> List[Plan]:
        """Search plans by status"""
        plans_data = await self.plan_repository.find_by_status(status)
        plans = []
        
        for plan_data in plans_data:
            try:
                plans.append(Plan(**plan_data))
            except Exception as e:
                print(f"Error creating Plan object from status search: {e}")
                continue
        
        return plans