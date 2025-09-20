import asyncio
import json
from dotenv import load_dotenv
from task_agent import TaskPlanningAgent

# Load environment variables
load_dotenv()

async def test_plan_creation():
    agent = TaskPlanningAgent()
    
    print("Testing plan creation with 'next week' goal...")
    plan = await agent.generate_plan("plan a trip on next week to pune", "A trip to Pune planned for next week")
    
    print(f"Plan ID: {plan.id}")
    print(f"Goal: {plan.goal}")
    print(f"Number of days: {len(plan.days)}")
    
    for day in plan.days:
        print(f"\nDay {day.day_number}:")
        print(f"  Date: {day.date}")
        print(f"  Summary: {day.summary}")
        for task in day.tasks:
            print(f"    Task ID: {task.id}")
            print(f"    Title: {task.title}")
            print(f"    Duration: {task.estimated_duration}")

if __name__ == "__main__":
    asyncio.run(test_plan_creation())