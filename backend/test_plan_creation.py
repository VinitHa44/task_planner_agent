import asyncio
import json
from task_agent import TaskPlanningAgent

async def test_plan_creation():
    agent = TaskPlanningAgent()
    
    print("Testing plan creation with proper IDs...")
    plan = await agent.generate_plan("Plan a day trip to Mumbai", "Sightseeing and food")
    
    print(f"Plan ID: {plan.id}")
    print(f"Goal: {plan.goal}")
    print(f"Number of days: {len(plan.days)}")
    
    for day in plan.days:
        print(f"\nDay {day.day_number}:")
        for task in day.tasks:
            print(f"  Task ID: {task.id}")
            print(f"  Title: {task.title}")
            print(f"  Duration: {task.estimated_duration}")

if __name__ == "__main__":
    asyncio.run(test_plan_creation())