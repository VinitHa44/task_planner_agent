"""
Main application file for AI Task Planning Agent
Implements FastAPI multi-layer architecture with clean separation of concerns
"""
from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config.database import db_manager
from config.settings import settings
from routers import plan_router, health_router

# Load environment variables from root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    """Database lifespan manager"""
    print(f"Starting {settings.APP_NAME}...")
    
    # Connect to database
    await db_manager.connect()
    
    yield
    
    # Cleanup on shutdown
    print(f"Shutting down {settings.APP_NAME}...")
    await db_manager.close()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=db_lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include routers
app.include_router(plan_router, prefix="/api/v1", tags=["Plans"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Task Planning Agent API", "version": settings.APP_VERSION}


# Legacy health endpoint for backward compatibility
@app.get("/health")
async def legacy_health_check():
    """Legacy health check endpoint for backward compatibility"""
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )