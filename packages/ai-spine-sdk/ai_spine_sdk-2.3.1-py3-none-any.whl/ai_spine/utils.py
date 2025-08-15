"""Utility functions for AI Spine SDK."""

import time
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from dateutil import parser as date_parser

from ai_spine.exceptions import TimeoutError, ValidationError

logger = logging.getLogger(__name__)


def validate_flow_id(flow_id: str) -> None:
    """Validate flow ID format.
    
    Args:
        flow_id: Flow identifier to validate
        
    Raises:
        ValidationError: If flow_id is invalid
    """
    if not flow_id:
        raise ValidationError("Flow ID cannot be empty")
    if not isinstance(flow_id, str):
        raise ValidationError(f"Flow ID must be a string, got {type(flow_id)}")


def validate_execution_id(execution_id: str) -> None:
    """Validate execution ID format.
    
    Args:
        execution_id: Execution identifier to validate
        
    Raises:
        ValidationError: If execution_id is invalid
    """
    if not execution_id:
        raise ValidationError("Execution ID cannot be empty")
    if not isinstance(execution_id, str):
        raise ValidationError(f"Execution ID must be a string, got {type(execution_id)}")


def validate_agent_id(agent_id: str) -> None:
    """Validate agent ID format.
    
    Args:
        agent_id: Agent identifier to validate
        
    Raises:
        ValidationError: If agent_id is invalid
    """
    if not agent_id:
        raise ValidationError("Agent ID cannot be empty")
    if not isinstance(agent_id, str):
        raise ValidationError(f"Agent ID must be a string, got {type(agent_id)}")


def validate_input_data(input_data: Dict[str, Any]) -> None:
    """Validate input data format.
    
    Args:
        input_data: Input data to validate
        
    Raises:
        ValidationError: If input_data is invalid
    """
    if input_data is None:
        raise ValidationError("Input data cannot be None")
    if not isinstance(input_data, dict):
        raise ValidationError(f"Input data must be a dictionary, got {type(input_data)}")


def parse_datetime(date_string: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string to datetime object.
    
    Args:
        date_string: ISO format datetime string
        
    Returns:
        Parsed datetime object or None if input is None/empty
    """
    if not date_string:
        return None
    try:
        return date_parser.isoparse(date_string)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime '{date_string}': {e}")
        return None


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        import random
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def poll_with_timeout(
    check_fn: Callable[[], tuple[bool, Any]],
    timeout: int = 300,
    interval: int = 2,
    timeout_message: Optional[str] = None
) -> Any:
    """Poll a function until it returns True or timeout occurs.
    
    Args:
        check_fn: Function that returns (is_done, result)
        timeout: Maximum time to wait in seconds
        interval: Polling interval in seconds
        timeout_message: Custom timeout error message
        
    Returns:
        Result from check_fn when is_done is True
        
    Raises:
        TimeoutError: If timeout is exceeded
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        is_done, result = check_fn()
        if is_done:
            return result
        
        remaining_time = timeout - (time.time() - start_time)
        sleep_time = min(interval, remaining_time)
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    message = timeout_message or f"Operation timed out after {timeout} seconds"
    raise TimeoutError(message, timeout=timeout)


def format_url(base_url: str, path: str, **path_params: str) -> str:
    """Format URL with base and path parameters.
    
    Args:
        base_url: Base API URL
        path: API path with optional placeholders
        **path_params: Path parameter values
        
    Returns:
        Formatted URL
    """
    # Remove trailing slash from base_url
    base_url = base_url.rstrip("/")
    
    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path
    
    # Replace path parameters
    for key, value in path_params.items():
        placeholder = "{" + key + "}"
        path = path.replace(placeholder, str(value))
    
    return base_url + path


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary.
    
    Args:
        data: Dictionary to clean
        
    Returns:
        Dictionary without None values
    """
    return {k: v for k, v in data.items() if v is not None}