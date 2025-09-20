import asyncio
import os
from dotenv import load_dotenv
from database import Database

async def test_database():
    load_dotenv()
    
    try:
        print("Testing database connection...")
        db = Database()
        
        print("Testing get_all_plans...")
        plans = await db.get_all_plans()
        print(f"Found {len(plans)} plans")
        
        for plan in plans:
            print(f"Plan ID: {plan.id}")
            print(f"Goal: {plan.goal}")
            print(f"Days: {len(plan.days)}")
            print("---")
        
        await db.close()
        print("✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())