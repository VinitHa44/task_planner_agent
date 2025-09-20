import os
import asyncio
from database import Database
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_database():
    """Setup database and create indexes"""
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "task_planning_db")]
    
    # Create indexes
    await db.plans.create_index("created_at")
    await db.plans.create_index("goal")
    
    print("Database setup completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_database())
