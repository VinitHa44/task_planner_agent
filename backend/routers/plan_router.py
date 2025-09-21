"""
Plan router - defines API endpoints for plan-related operations
"""
import time
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from models.schemas import (
    PlanCreateRequest,
    PlanUpdateRequest,
    PlanResponse,
    PlanListResponse
)
from controllers import PlanController
from utils.error_handler import handle_exceptions

# Create router instance
router = APIRouter()


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_plan(
    plan_request: PlanCreateRequest,
    plan_controller: PlanController = Depends(PlanController)
):
    """Create a new task plan from a natural language goal"""
    # Simplified logging - detailed logs now in trip files
    start_time = time.time()
    
    try:
        response = await plan_controller.create_plan(plan_request)
        print(f"✅ Plan created in {time.time() - start_time:.2f}s")
        return response
        
    except Exception as e:
        print(f"❌ Plan creation failed: {str(e)}")
        raise


@router.get("/plans", response_model=PlanListResponse)
@handle_exceptions
async def get_all_plans(
    limit: Optional[int] = Query(None, description="Maximum number of plans to return"),
    offset: Optional[int] = Query(None, description="Number of plans to skip"),
    plan_controller: PlanController = Depends(PlanController)
):
    """Get all saved plans"""
    return await plan_controller.get_all_plans(limit=limit, offset=offset)


@router.get("/plans/search", response_model=PlanListResponse)
@handle_exceptions
async def search_plans(
    goal: str = Query(..., description="Goal pattern to search for"),
    plan_controller: PlanController = Depends(PlanController)
):
    """Search plans by goal pattern"""
    return await plan_controller.search_plans_by_goal(goal)


@router.get("/plans/{plan_id}", response_model=PlanResponse)
@handle_exceptions
async def get_plan(
    plan_id: str,
    plan_controller: PlanController = Depends(PlanController)
):
    """Get a specific plan by ID"""
    return await plan_controller.get_plan(plan_id)


@router.put("/plans/{plan_id}", response_model=PlanResponse)
@handle_exceptions
async def update_plan(
    plan_id: str,
    plan_update: PlanUpdateRequest,
    plan_controller: PlanController = Depends(PlanController)
):
    """Update a plan"""
    return await plan_controller.update_plan(plan_id, plan_update)


@router.patch("/plans/{plan_id}/status")
@handle_exceptions
async def update_plan_status(
    plan_id: str,
    status: str = Query(..., description="New status for the plan"),
    plan_controller: PlanController = Depends(PlanController)
):
    """Update only the status of a plan"""
    return await plan_controller.update_plan_status(plan_id, status)


@router.delete("/plans/{plan_id}")
@handle_exceptions
async def delete_plan(
    plan_id: str,
    plan_controller: PlanController = Depends(PlanController)
):
    """Delete a plan"""
    return await plan_controller.delete_plan(plan_id)