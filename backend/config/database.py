"""
Database configuration and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config.settings import settings

class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Connect to database"""
        print("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.database = self.client[settings.DATABASE_NAME]
        print("Database connected successfully!")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("Database connection closed.")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database

# Global database manager instance
db_manager = DatabaseManager()