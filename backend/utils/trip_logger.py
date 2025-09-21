"""
Trip-specific logging system that creates individual log files for each trip
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import json
from typing import Any, Dict, Optional
import re

class TripLogger:
    """Logger that creates individual log files for each trip"""
    
    def __init__(self):
        self.base_log_dir = Path("logs/trips")
        self.base_log_dir.mkdir(parents=True, exist_ok=True)
        
    def _create_logger(self, name: str, file_path: str) -> logging.Logger:
        """Create a logger with file handler"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        logger.propagate = False
        
        return logger
    
    def create_trip_logger(self, goal: str, trip_id: str = None) -> logging.Logger:
        """Create a specific logger for a trip"""
        # Create safe filename from goal
        safe_goal = self._create_safe_filename(goal)
        
        # Add timestamp and trip_id if available
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if trip_id:
            filename = f"{timestamp}_{safe_goal}_{trip_id[:8]}.log"
        else:
            filename = f"{timestamp}_{safe_goal}.log"
        
        log_path = self.base_log_dir / filename
        
        logger_name = f"trip_{timestamp}_{safe_goal}"
        logger = self._create_logger(logger_name, str(log_path))
        
        # Log trip start header
        logger.info("=" * 80)
        logger.info(f"TRIP LOG STARTED: {goal}")
        logger.info(f"Trip ID: {trip_id or 'Generated'}")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        return logger
    
    def _create_safe_filename(self, goal: str) -> str:
        """Create safe filename from goal text"""
        # Remove special characters and limit length
        safe_goal = re.sub(r'[^\w\s-]', '', goal)
        safe_goal = re.sub(r'[-\s]+', '_', safe_goal)
        return safe_goal[:50].strip('_')
    
    def log_structured_data(self, logger: logging.Logger, level: str, message: str, data: Any = None):
        """Log structured data with proper formatting"""
        if data:
            if isinstance(data, (dict, list)):
                try:
                    formatted_data = json.dumps(data, indent=2, default=str, ensure_ascii=False)
                    log_message = f"{message}\n{formatted_data}"
                except Exception:
                    log_message = f"{message}\n{str(data)}"
            else:
                log_message = f"{message}: {data}"
        else:
            log_message = message
        
        # Log based on level
        if level.lower() == 'debug':
            logger.debug(log_message)
        elif level.lower() == 'info':
            logger.info(log_message)
        elif level.lower() == 'warning':
            logger.warning(log_message)
        elif level.lower() == 'error':
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    def log_step(self, logger: logging.Logger, step: str, details: str = None):
        """Log a processing step"""
        step_message = f"🔄 STEP: {step}"
        if details:
            step_message += f" - {details}"
        logger.info(step_message)
    
    def log_success(self, logger: logging.Logger, message: str, data: Any = None):
        """Log successful operation"""
        self.log_structured_data(logger, 'info', f"✅ SUCCESS: {message}", data)
    
    def log_error(self, logger: logging.Logger, message: str, error: Exception = None, data: Any = None):
        """Log error with details"""
        error_message = f"❌ ERROR: {message}"
        if error:
            error_message += f" - {str(error)}"
        self.log_structured_data(logger, 'error', error_message, data)
    
    def log_warning(self, logger: logging.Logger, message: str, data: Any = None):
        """Log warning"""
        self.log_structured_data(logger, 'warning', f"⚠️ WARNING: {message}", data)
    
    def log_api_call(self, logger: logging.Logger, service: str, method: str, params: Dict = None, response: Any = None):
        """Log API call details"""
        logger.info(f"🌐 API CALL: {service}.{method}")
        if params:
            self.log_structured_data(logger, 'info', "📤 Request Parameters", params)
        if response:
            self.log_structured_data(logger, 'info', "📥 Response", response)
    
    def finalize_trip_log(self, logger: logging.Logger, success: bool = True, summary: str = None):
        """Finalize trip log with summary"""
        logger.info("=" * 80)
        if success:
            logger.info("✅ TRIP PLANNING COMPLETED SUCCESSFULLY")
        else:
            logger.info("❌ TRIP PLANNING FAILED")
        
        if summary:
            logger.info(f"Summary: {summary}")
        
        logger.info(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

# Global trip logger instance
trip_logger = TripLogger()

def get_trip_logger(goal: str, trip_id: str = None) -> logging.Logger:
    """Get trip logger instance"""
    return trip_logger.create_trip_logger(goal, trip_id)