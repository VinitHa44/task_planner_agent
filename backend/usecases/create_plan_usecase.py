"""
Plan creation use case - orchestrates the business logic for creating new plans
"""
from typing import Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import Depends
import logging

from models.domain import Plan
from repositories import PlanRepository
from usecases.create_plan_usecase_helper import CreatePlanUsecaseHelper
from utils.trip_logger import get_trip_logger, trip_logger

class CreatePlanUseCase:
    """Use case for creating new travel plans"""
    
    def __init__(self, 
                 plan_repository: PlanRepository = Depends(PlanRepository),
                 create_plan_helper: CreatePlanUsecaseHelper = Depends(CreatePlanUsecaseHelper)):
        self.plan_repository = plan_repository
        self.create_plan_helper = create_plan_helper
    
    async def execute(self, goal: str, description: str = None) -> Plan:
        """Execute the plan creation workflow"""
        
        # Create trip-specific logger
        logger = get_trip_logger(goal)
        
        try:
            trip_logger.log_step(logger, "Plan Creation Started", f"Goal: {goal}")
            
            # Step 1: Extract key information from the goal
            trip_logger.log_step(logger, "Step 1 - Extracting goal information")
            extracted_info = await self.create_plan_helper.extract_goal_info(goal)
            extracted_info["goal"] = goal  # Add the original goal for date calculation
            trip_logger.log_structured_data(logger, 'info', "📤 Extracted Information", extracted_info)
            
            # Step 2: Gather external information
            trip_logger.log_step(logger, "Step 2 - Gathering external information")
            external_info = await self.create_plan_helper.gather_external_info(extracted_info)
            trip_logger.log_structured_data(logger, 'info', "📤 External Information", external_info)
            
            # Step 3: Generate the plan using AI with today's date for context
            trip_logger.log_step(logger, "Step 3 - Generating plan with AI")
            today = datetime.now()
            logger.info(f"� Current date: {today.strftime('%Y-%m-%d %H:%M:%S')}")
            plan_data = await self.create_plan_helper.generate_plan_with_ai(goal, description, extracted_info, external_info, today)
            trip_logger.log_structured_data(logger, 'info', "📤 Generated Plan Data", plan_data)
            
            # Step 4: Enrich plan with external information and convert to domain model
            trip_logger.log_step(logger, "Step 4 - Enriching plan with external data")
            enriched_plan = await self.create_plan_helper.enrich_plan_with_external_data(plan_data, external_info, goal)
            logger.info(f"� Enriched plan type: {type(enriched_plan)}")
            
            # Step 5: Save to repository
            trip_logger.log_step(logger, "Step 5 - Saving plan to database")
            plan_dict = enriched_plan.dict()
            plan_id = await self.plan_repository.create(plan_dict)
            logger.info(f"� Plan saved with ID: {plan_id}")
            enriched_plan.id = plan_id
            
            trip_logger.log_success(logger, "Plan creation completed successfully", {
                "plan_id": plan_id,
                "goal": goal,
                "duration": enriched_plan.total_duration,
                "days_count": len(enriched_plan.days)
            })
            
            trip_logger.finalize_trip_log(logger, success=True, summary=f"Created {len(enriched_plan.days)}-day plan for '{goal}'")
            return enriched_plan
            
        except Exception as e:
            trip_logger.log_error(logger, "Plan creation failed", e, {
                "goal": goal,
                "description": description,
                "error_type": type(e).__name__
            })
            trip_logger.finalize_trip_log(logger, success=False, summary=f"Failed to create plan: {str(e)}")
            raise