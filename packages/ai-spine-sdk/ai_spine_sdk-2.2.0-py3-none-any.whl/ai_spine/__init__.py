"""AI Spine SDK for Python.

A pythonic interface for AI agent orchestration.
"""

from ai_spine.__version__ import __version__
from ai_spine.client import AISpine
from ai_spine.client import AISpine as Client  # Alias for compatibility
from ai_spine.exceptions import (
    AISpineError,
    AuthenticationError,
    ValidationError,
    ExecutionError,
    TimeoutError,
    RateLimitError,
    InsufficientCreditsError,
    NetworkError,
    APIError,
)

__all__ = [
    "__version__",
    "AISpine",
    "Client",
    "AISpineError",
    "AuthenticationError",
    "ValidationError",
    "ExecutionError",
    "TimeoutError",
    "RateLimitError",
    "InsufficientCreditsError",
    "NetworkError",
    "APIError",
]