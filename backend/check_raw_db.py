import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_raw_database():
    load_dotenv()
    
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "task_planning_db")]
    
    print("Raw database records:")
    async for plan in db.plans.find().limit(2):
        print(f"Raw plan _id: {plan.get('_id')}")
        print(f"Raw plan id: {plan.get('id')}")
        print(f"Raw plan goal: {plan.get('goal', '')[:50]}...")
        
        if 'days' in plan and plan['days']:
            first_day = plan['days'][0]
            if 'tasks' in first_day and first_day['tasks']:
                first_task = first_day['tasks'][0]
                print(f"First task id: {first_task.get('id')}")
                print(f"First task title: {first_task.get('title', '')[:30]}...")
        print("---")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_raw_database())