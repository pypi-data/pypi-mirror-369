"""Custom exceptions for AI Spine SDK."""

from typing import Optional, Dict, Any


class AISpineError(Exception):
    """Base exception for AI Spine SDK."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(AISpineError):
    """Raised when authentication fails."""
    pass


class ValidationError(AISpineError):
    """Raised when input validation fails."""
    pass


class ExecutionError(AISpineError):
    """Raised when flow execution fails."""
    
    def __init__(
        self, 
        message: str, 
        execution_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.execution_id = execution_id


class TimeoutError(AISpineError):
    """Raised when operation times out."""
    
    def __init__(
        self, 
        message: str, 
        timeout: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.timeout = timeout


class RateLimitError(AISpineError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.retry_after = retry_after


class InsufficientCreditsError(AISpineError):
    """Raised when user has insufficient credits."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.credits_needed = details.get("credits_needed") if details else None
        self.credits_available = details.get("credits_available") if details else None


class NetworkError(AISpineError):
    """Raised when network-related errors occur."""
    pass


class APIError(AISpineError):
    """Raised when API returns an error response."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body