"""Constants for AI Spine SDK."""

# Default API configuration
DEFAULT_BASE_URL = "https://ai-spine-api-production.up.railway.app"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_POLLING_INTERVAL = 2  # seconds
DEFAULT_EXECUTION_TIMEOUT = 300  # seconds (5 minutes)

# API Endpoints
ENDPOINTS = {
    # Flow endpoints
    "execute_flow": "/flows/execute",
    "get_execution": "/executions/{execution_id}",
    "list_flows": "/flows",
    "get_flow": "/flows/{flow_id}",
    
    # Agent endpoints
    "list_agents": "/agents",
    "create_agent": "/agents",
    "delete_agent": "/agents/{agent_id}",
    
    # System endpoints
    "health": "/health",
    "metrics": "/metrics",
    "status": "/status",
}

# Execution statuses
EXECUTION_STATUS = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
}

# Terminal execution statuses (no more changes expected)
TERMINAL_STATUSES = {
    EXECUTION_STATUS["COMPLETED"],
    EXECUTION_STATUS["FAILED"],
    EXECUTION_STATUS["CANCELLED"],
}

# HTTP Status codes for retry
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# Request headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}