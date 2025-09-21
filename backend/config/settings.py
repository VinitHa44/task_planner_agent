"""
Application settings and configuration management
"""
import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Task Planning Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "task_planning_db"
    
    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    WEB_SEARCH_API_KEY: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()