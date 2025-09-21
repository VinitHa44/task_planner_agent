"""
Logging configuration and utilities
"""
import logging
import sys
from config.settings import settings

def setup_logging():
    """Configure application logging"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create application logger
    logger = logging.getLogger(settings.APP_NAME)
    return logger

# Global logger instance
logger = setup_logging()