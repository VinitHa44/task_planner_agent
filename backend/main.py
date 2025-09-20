from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from dotenv import load_dotenv

from models import Plan, PlanCreate, PlanResponse
from task_agent import TaskPlanningAgent
from database import Database

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Task Planning Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - will be initialized on startup
task_agent = None
db = None

@app.on_event("startup")
async def startup_event():
    global task_agent, db
    print("Starting AI Task Planning Agent...")
    try:
        print("Initializing database connection...")
        db = Database()
        print("Database connected successfully!")
        
        print("Initializing task agent...")
        task_agent = TaskPlanningAgent()
        print("Task agent initialized successfully!")
        
        print("AI Task Planning Agent startup complete!")
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        traceback.print_exc()

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()

@app.get("/")
async def root():
    return {"message": "AI Task Planning Agent API", "version": "1.0.0"}

@app.post("/plans", response_model=PlanResponse)
async def create_plan(plan_request: PlanCreate):
    """Create a new task plan from a natural language goal"""
    try:
        if task_agent is None:
            raise HTTPException(status_code=503, detail="Task agent not initialized")
        if db is None:
            raise HTTPException(status_code=503, detail="Database not initialized")
            
        print(f"Creating plan for goal: {plan_request.goal}")
        
        # Generate plan using AI agent
        plan = await task_agent.generate_plan(plan_request.goal, plan_request.description)
        print(f"Plan generated successfully: {plan.goal}")
        
        # Save to database
        plan_id = await db.create_plan(plan)
        plan.id = plan_id
        print(f"Plan saved with ID: {plan_id}")
        
        return PlanResponse(**plan.dict())
    except Exception as e:
        print(f"Error in create_plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating plan: {str(e)}")

@app.get("/plans", response_model=List[PlanResponse])
async def get_all_plans():
    """Get all saved plans"""
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not initialized")
        plans = await db.get_all_plans()
        
        # Ensure each plan has a valid ID before converting to PlanResponse
        response_plans = []
        for plan in plans:
            plan_dict = plan.dict()
            # Ensure ID is a valid string
            if not plan_dict.get("id") or plan_dict["id"] is None:
                from bson import ObjectId
                plan_dict["id"] = str(ObjectId())
            response_plans.append(PlanResponse(**plan_dict))
        
        return response_plans
    except Exception as e:
        print(f"Error in get_all_plans: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving plans: {str(e)}")

@app.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """Get a specific plan by ID"""
    try:
        plan = await db.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return PlanResponse(**plan.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plan: {str(e)}")

@app.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: str, plan: Plan):
    """Update a plan"""
    try:
        success = await db.update_plan(plan_id, plan)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        updated_plan = await db.get_plan(plan_id)
        return PlanResponse(**updated_plan.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")

@app.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a plan"""
    try:
        success = await db.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"message": "Plan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting plan: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Task Planning Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)))

