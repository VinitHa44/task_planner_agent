"""
Error handling utilities and custom exceptions
"""
import functools
from typing import Any, Dict, Callable
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import traceback

class PlanNotFoundError(Exception):
    """Raised when a plan is not found"""
    pass

class ExternalServiceError(Exception):
    """Raised when an external service fails"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

"""
Error handling utilities and custom exceptions
"""
import functools
from typing import Any, Dict, Callable
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import traceback
from utils.trip_logger import TripLogger

class PlanNotFoundError(Exception):
    """Raised when a plan is not found"""
    pass

class ExternalServiceError(Exception):
    """Raised when an external service fails"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions in route handlers"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = kwargs.get('logger')  # Try to get logger from kwargs
        
        try:
            if logger:
                logger.log_step(f"🔄 Executing function: {func.__name__}", {})
            
            result = await func(*args, **kwargs)
            
            if logger:
                logger.log_success(f"Function {func.__name__} completed successfully", {
                    "result_type": type(result).__name__
                })
            
            return result
        except HTTPException as e:
            if logger:
                logger.log_error(f"HTTPException in {func.__name__}", {
                    "status_code": e.status_code,
                    "detail": str(e.detail)
                })
            raise
        except PlanNotFoundError as e:
            if logger:
                logger.log_error(f"PlanNotFoundError in {func.__name__}", {"error": str(e)})
            raise HTTPException(status_code=404, detail="Plan not found")
        except ExternalServiceError as e:
            if logger:
                logger.log_error(f"ExternalServiceError in {func.__name__}", {"error": str(e)})
            raise HTTPException(status_code=503, detail="External service unavailable")
        except ValidationError as e:
            if logger:
                logger.log_error(f"ValidationError in {func.__name__}", {"error": str(e)})
            raise HTTPException(status_code=422, detail="Validation error")
        except Exception as e:
            error_message = str(e)
            
            if logger:
                logger.log_error(f"Exception in {func.__name__}", {
                    "error_type": type(e).__name__,
                    "error_message": error_message,
                    "error_args": str(e.args)
                })
            
            # Handle quota exceeded errors from Gemini API
            if "429" in error_message and "quota" in error_message.lower():
                import re
                retry_after = None
                
                # Extract retry delay if available
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_message)
                if retry_match:
                    retry_after = int(float(retry_match.group(1)))
                
                if logger:
                    logger.log_error("QUOTA_EXCEEDED error detected", {
                        "retry_after": retry_after,
                        "technical_details": error_message
                    })
                
                error_detail = {
                    "error": {
                        "type": "QUOTA_EXCEEDED",
                        "message": "AI service quota exceeded. Please try again later.",
                        "technical_details": error_message,
                        "retry_after": retry_after
                    },
                    "success": False
                }
                
                raise HTTPException(status_code=429, detail=error_detail)
            
            # Handle rate limiting errors
            elif "rate limit" in error_message.lower():
                if logger:
                    logger.log_error("RATE_LIMITED error detected", {
                        "technical_details": error_message
                    })
                
                error_detail = {
                    "error": {
                        "type": "RATE_LIMITED", 
                        "message": "Too many requests. Please wait a moment and try again.",
                        "technical_details": error_message
                    },
                    "success": False
                }
                
                raise HTTPException(status_code=429, detail=error_detail)
            
            if logger:
                logger.log_error(f"Unexpected error in {func.__name__}", {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
            
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application"""
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    if isinstance(exc, PlanNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": "Plan not found"}
        )
    
    if isinstance(exc, ExternalServiceError):
        return JSONResponse(
            status_code=503,
            content={"detail": "External service unavailable"}
        )
    
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error"}
        )
    
    # Note: Log unexpected errors - detailed logging now in trip files
    print(f"❌ Unexpected global error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

def create_error_response(status_code: int, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
    
    return response