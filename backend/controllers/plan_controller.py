"""
Plan controller - handles request/response processing and orchestration for plan-related operations
"""
from typing import List, Optional
from fastapi import HTTPException, Depends

from models.schemas import (
    PlanCreateRequest,
    PlanUpdateRequest, 
    PlanResponse,
    PlanListResponse
)
from models.domain import Plan
from usecases import (
    CreatePlanUseCase,
    GetPlanUseCase,
    GetAllPlansUseCase,
    SearchPlansUseCase,
    UpdatePlanUseCase,
    DeletePlanUseCase,
    UpdatePlanStatusUseCase
)

class PlanController:
    """Controller for plan-related operations"""
    
    def __init__(self, 
                 create_plan_usecase: CreatePlanUseCase = Depends(),
                 get_plan_usecase: GetPlanUseCase = Depends(),
                 get_all_plans_usecase: GetAllPlansUseCase = Depends(),
                 search_plans_usecase: SearchPlansUseCase = Depends(),
                 update_plan_usecase: UpdatePlanUseCase = Depends(),
                 delete_plan_usecase: DeletePlanUseCase = Depends(),
                 update_plan_status_usecase: UpdatePlanStatusUseCase = Depends()):
        self.create_plan_usecase = create_plan_usecase
        self.get_plan_usecase = get_plan_usecase
        self.get_all_plans_usecase = get_all_plans_usecase
        self.search_plans_usecase = search_plans_usecase
        self.update_plan_usecase = update_plan_usecase
        self.delete_plan_usecase = delete_plan_usecase
        self.update_plan_status_usecase = update_plan_status_usecase
    
    async def create_plan(self, request: PlanCreateRequest) -> PlanResponse:
        """Create a new plan"""
        try:
            # Execute the use case - detailed logging now in trip files
            plan = await self.create_plan_usecase.execute(request.goal, request.description)
            
            # Convert to response model
            response = self._convert_to_response(plan)
            return response
            
        except Exception as e:
            print(f"❌ Plan creation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")
    
    async def get_plan(self, plan_id: str) -> PlanResponse:
        """Get a plan by ID"""
        try:
            plan = await self.get_plan_usecase.execute(plan_id)
            
            if not plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            return self._convert_to_response(plan)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving plan: {str(e)}")
    
    async def get_all_plans(self, limit: Optional[int] = None, offset: Optional[int] = None) -> PlanListResponse:
        """Get all plans with optional pagination"""
        try:
            plans = await self.get_all_plans_usecase.execute(limit=limit, offset=offset)
            
            # Convert to response models
            plan_responses = []
            for plan in plans:
                try:
                    # Ensure each plan has a valid ID before converting to PlanResponse
                    if not plan.id or plan.id is None:
                        from bson import ObjectId
                        plan.id = str(ObjectId())
                    plan_responses.append(self._convert_to_response(plan))
                except Exception as e:
                    continue  # Skip invalid plans
            
            return PlanListResponse(plans=plan_responses, total=len(plan_responses))
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving plans: {str(e)}")
    
    async def update_plan(self, plan_id: str, request: PlanUpdateRequest) -> PlanResponse:
        """Update a plan"""
        try:
            # Get the current plan
            current_plan = await self.get_plan_usecase.execute(plan_id)
            if not current_plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            # Update only the fields that are provided
            if request.goal is not None:
                current_plan.goal = request.goal
            if request.description is not None:
                current_plan.description = request.description
            if request.days is not None:
                # Convert schema days to domain days
                from models.domain import Day, Task, TaskStatus
                domain_days = []
                for day_schema in request.days:
                    domain_tasks = []
                    for task_schema in day_schema.tasks:
                        domain_task = Task(
                            id=task_schema.id,
                            title=task_schema.title,
                            description=task_schema.description,
                            status=TaskStatus(task_schema.status),
                            estimated_duration=task_schema.estimated_duration,
                            external_info=task_schema.external_info,
                            created_at=task_schema.created_at
                        )
                        domain_tasks.append(domain_task)
                    
                    domain_day = Day(
                        day_number=day_schema.day_number,
                        date=day_schema.date,
                        tasks=domain_tasks,
                        summary=day_schema.summary,
                        weather_info=day_schema.weather_info
                    )
                    domain_days.append(domain_day)
                
                current_plan.days = domain_days
            
            if request.status is not None:
                current_plan.status = request.status
            
            # Execute the update
            updated_plan = await self.update_plan_usecase.execute(plan_id, current_plan)
            
            if not updated_plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            return self._convert_to_response(updated_plan)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")
    
    async def delete_plan(self, plan_id: str) -> dict:
        """Delete a plan"""
        try:
            success = await self.delete_plan_usecase.execute(plan_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            return {"message": "Plan deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting plan: {str(e)}")
    
    async def search_plans_by_goal(self, goal_pattern: str) -> PlanListResponse:
        """Search plans by goal pattern"""
        try:
            plans = await self.search_plans_usecase.search_by_goal(goal_pattern)
            
            plan_responses = []
            for plan in plans:
                try:
                    plan_responses.append(self._convert_to_response(plan))
                except Exception as e:
                    continue  # Skip invalid plans
            
            return PlanListResponse(plans=plan_responses, total=len(plan_responses))
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching plans: {str(e)}")
    
    async def update_plan_status(self, plan_id: str, new_status: str) -> PlanResponse:
        """Update only the status of a plan"""
        try:
            updated_plan = await self.update_plan_status_usecase.execute(plan_id, new_status)
            
            if not updated_plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            return self._convert_to_response(updated_plan)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating plan status: {str(e)}")
    
    def _convert_to_response(self, plan: Plan) -> PlanResponse:
        """Convert domain Plan to API response schema"""
        try:
            # Convert domain model to dict with proper serialization
            plan_dict = plan.model_dump(mode='json')
            
            # Ensure ID is present and valid
            if not plan_dict.get("id") or plan_dict["id"] is None:
                from bson import ObjectId
                plan_dict["id"] = str(ObjectId())
            
            # Create response using the schema
            return PlanResponse(**plan_dict)
            
        except Exception as e:
            # Note: Error details logged in trip files
            raise