"""Error handling utilities"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class SupportAgentError(Exception):
    """Base exception for support agent errors"""
    pass


class IntegrationError(SupportAgentError):
    """Exception for integration errors"""
    pass


class ValidationError(SupportAgentError):
    """Exception for validation errors"""
    pass


class ConfigurationError(SupportAgentError):
    """Exception for configuration errors"""
    pass


def handle_integration_error(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle integration errors and return user-friendly error response
    
    Args:
        error: The exception that occurred
        context: Optional context about where the error occurred
    
    Returns:
        Dictionary with error information
    """
    error_info = {
        "error": True,
        "message": str(error),
        "type": type(error).__name__
    }
    
    if context:
        error_info["context"] = context
    
    logger.error(f"Integration error{f' in {context}' if context else ''}: {error}", exc_info=True)
    
    return error_info


def handle_validation_error(error: Exception, field: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle validation errors
    
    Args:
        error: The validation exception
        field: Optional field name that failed validation
    
    Returns:
        Dictionary with validation error information
    """
    error_info = {
        "error": True,
        "message": str(error),
        "type": "ValidationError"
    }
    
    if field:
        error_info["field"] = field
    
    logger.warning(f"Validation error{f' for field {field}' if field else ''}: {error}")
    
    return error_info


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        import asyncio
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def safe_execute(func: Callable, default_value: Any = None, *args, **kwargs) -> Any:
    """
    Safely execute a function and return default value on error
    
    Args:
        func: Function to execute
        default_value: Value to return on error
        *args, **kwargs: Arguments to pass to function
    
    Returns:
        Function result or default_value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}", exc_info=True)
        return default_value

