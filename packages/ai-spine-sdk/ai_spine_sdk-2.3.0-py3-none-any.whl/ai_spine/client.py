"""Main client for AI Spine SDK."""

import json
import logging
import time
import warnings
from typing import Optional, Dict, Any, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ai_spine.__version__ import __version__
from ai_spine.constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_EXECUTION_TIMEOUT,
    DEFAULT_HEADERS,
    ENDPOINTS,
    RETRY_STATUS_CODES,
    TERMINAL_STATUSES,
)
from ai_spine.exceptions import (
    AISpineError,
    AuthenticationError,
    ValidationError,
    ExecutionError,
    TimeoutError,
    RateLimitError,
    NetworkError,
    APIError,
    InsufficientCreditsError,
)
from ai_spine.utils import (
    validate_flow_id,
    validate_execution_id,
    validate_agent_id,
    validate_input_data,
    format_url,
    clean_dict,
    poll_with_timeout,
)

logger = logging.getLogger(__name__)


class AISpine:
    """AI Spine SDK client for Python.
    
    Args:
        api_key: API key for authentication (required)
        base_url: API base URL (defaults to production)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        debug: Enable debug logging (default: False)
    
    Example:
        >>> client = AISpine(api_key="sk_your_api_key_here")
        >>> result = client.execute_flow('credit_analysis', {'amount': 50000})
        >>> execution = client.wait_for_execution(result['execution_id'])
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        debug: bool = False
    ):
        # Validate API key
        if not api_key:
            raise ValueError("API key is required")
        if not api_key.startswith("sk_"):
            warnings.warn("API key should start with 'sk_'. Make sure you're using a valid user key.")
        
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.debug = debug
        
        # Configure logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # Configure session with retry strategy
        self.session = self._create_session(max_retries)
        
    def _create_session(self, max_retries: int) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        
        # Add retry strategy
        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=1,
                status_forcelist=RETRY_STATUS_CODES,
                allowed_methods=["GET", "POST", "PUT", "DELETE"],
            )
        else:
            # No retries - don't use status_forcelist
            retry_strategy = Retry(total=0, read=0, connect=0)
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = f"ai-spine-sdk-python/{__version__}"
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Content-Type"] = "application/json"
        session.headers.update(headers)
            
        return session
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
        **path_params: str
    ) -> Dict[str, Any]:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            auth_required: Whether to include authentication headers
            **path_params: Path parameters to replace in endpoint
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various AISpineError subclasses based on response
        """
        url = format_url(self.base_url, endpoint, **path_params)
        
        if self.debug:
            logger.debug(f"{method} {url}")
            if data:
                logger.debug(f"Request body: {json.dumps(data, indent=2)}")
        
        try:
            # Prepare headers
            headers = None
            if not auth_required:
                # For unauthenticated requests, use headers without Authorization
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": f"ai-spine-sdk-python/{__version__}"
                }
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                headers=headers  # Override session headers if provided
            )
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response body: {response.text}")
            
            # Handle successful response
            if response.status_code < 300:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # Some endpoints might return empty response
                    if response.status_code == 204 or not response.text:
                        return {}
                    raise AISpineError(f"Invalid JSON response: {response.text}")
            
            # Handle error responses
            self._handle_error_response(response)
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error HTTP responses.
        
        Args:
            response: HTTP response object
            
        Raises:
            Appropriate AISpineError subclass
        """
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
            details = error_data.get("details", error_data)  # Use full error_data as details if no explicit details field
        except json.JSONDecodeError:
            message = response.text or f"HTTP {response.status_code}"
            details = {}
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key. Get your key from https://ai-spine.com/dashboard", details)
        elif response.status_code == 403:
            # Check if it's specifically a credits issue
            error_code = details.get("error_code", "").upper() if isinstance(details, dict) else ""
            if "INSUFFICIENT_CREDITS" in error_code or "credits" in message.lower():
                raise InsufficientCreditsError("No credits remaining. Top up at https://ai-spine.com/billing", details)
            raise APIError(message, status_code=response.status_code, response_body=response.text, details=details)
        elif response.status_code == 400:
            raise ValidationError(message, details)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError("Rate limit exceeded. Please wait before retrying.", retry_after=int(retry_after) if retry_after else None, details=details)
        elif response.status_code >= 500:
            raise APIError(message, status_code=response.status_code, response_body=response.text, details=details)
        else:
            raise APIError(message, status_code=response.status_code, response_body=response.text, details=details)
    
    # Flow Execution Methods
    
    def execute_flow(
        self,
        flow_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an AI Spine flow.
        
        Args:
            flow_id: Unique identifier of the flow to execute
            input_data: Input data for the flow execution
            metadata: Optional metadata to attach to the execution
        
        Returns:
            Dictionary containing:
                - execution_id (str): Unique execution identifier
                - status (str): Initial status ('pending')
                - created_at (str): ISO timestamp of creation
        
        Raises:
            ValidationError: If flow_id or input_data is invalid
            AuthenticationError: If API key is invalid
            ExecutionError: If flow execution fails
            requests.RequestException: If network request fails
        
        Example:
            >>> client = AISpine()
            >>> result = client.execute_flow(
            ...     'sentiment-analysis',
            ...     {'text': 'This product is amazing!'}
            ... )
            >>> print(result['execution_id'])
            'exec-123abc'
        """
        validate_flow_id(flow_id)
        validate_input_data(input_data)
        
        request_data = {
            "flow_id": flow_id,
            "input_data": input_data,
        }
        
        if metadata:
            request_data["metadata"] = metadata
        
        return self._request("POST", ENDPOINTS["execute_flow"], data=request_data)
    
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status and results.
        
        Args:
            execution_id: Unique execution identifier
            
        Returns:
            Dictionary containing execution details
            
        Raises:
            ValidationError: If execution_id is invalid
            APIError: If execution not found
        """
        validate_execution_id(execution_id)
        return self._request("GET", ENDPOINTS["get_execution"], execution_id=execution_id)
    
    def wait_for_execution(
        self,
        execution_id: str,
        timeout: int = DEFAULT_EXECUTION_TIMEOUT,
        interval: int = DEFAULT_POLLING_INTERVAL
    ) -> Dict[str, Any]:
        """Wait for execution to complete.
        
        Args:
            execution_id: Unique execution identifier
            timeout: Maximum time to wait in seconds (default: 300)
            interval: Polling interval in seconds (default: 2)
            
        Returns:
            Final execution result
            
        Raises:
            TimeoutError: If execution doesn't complete within timeout
            ExecutionError: If execution fails
        """
        validate_execution_id(execution_id)
        
        def check_execution():
            result = self.get_execution(execution_id)
            status = result.get("status")
            
            if status in TERMINAL_STATUSES:
                if status == "failed":
                    error_msg = result.get("error_message", "Execution failed")
                    raise ExecutionError(error_msg, execution_id=execution_id, details=result)
                return True, result
            
            return False, None
        
        return poll_with_timeout(
            check_execution,
            timeout=timeout,
            interval=interval,
            timeout_message=f"Execution {execution_id} timed out after {timeout} seconds"
        )
    
    def cancel_execution(self, execution_id: str) -> Dict[str, Any]:
        """Cancel a running execution.
        
        Args:
            execution_id: Unique execution identifier
            
        Returns:
            Updated execution status
            
        Raises:
            ValidationError: If execution_id is invalid
            APIError: If execution cannot be cancelled
        """
        validate_execution_id(execution_id)
        return self._request(
            "POST",
            f"/executions/{execution_id}/cancel",
            execution_id=execution_id
        )
    
    # Flow Management Methods
    
    def list_flows(self) -> List[Dict[str, Any]]:
        """List all available flows.
        
        Returns:
            List of flow dictionaries
        """
        response = self._request("GET", ENDPOINTS["list_flows"])
        # Handle both array and object with 'flows' key responses
        if isinstance(response, list):
            return response
        return response.get("flows", [])
    
    def get_flow(self, flow_id: str) -> Dict[str, Any]:
        """Get flow details by ID.
        
        Args:
            flow_id: Unique flow identifier
            
        Returns:
            Flow details dictionary
            
        Raises:
            ValidationError: If flow_id is invalid
            APIError: If flow not found
        """
        validate_flow_id(flow_id)
        return self._request("GET", ENDPOINTS["get_flow"], flow_id=flow_id)
    
    # Agent Management Methods
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents.
        
        Returns:
            List of agent dictionaries
        """
        response = self._request("GET", ENDPOINTS["list_agents"])
        # Handle both array and object with 'agents' key responses
        if isinstance(response, list):
            return response
        return response.get("agents", [])
    
    def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent.
        
        Args:
            agent_config: Agent configuration dictionary
            
        Returns:
            Created agent details
            
        Raises:
            ValidationError: If agent_config is invalid
        """
        if not agent_config:
            raise ValidationError("Agent configuration cannot be empty")
        
        return self._request("POST", ENDPOINTS["create_agent"], data=agent_config)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_id: Unique agent identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValidationError: If agent_id is invalid
            APIError: If agent not found
        """
        validate_agent_id(agent_id)
        
        try:
            self._request("DELETE", ENDPOINTS["delete_agent"], agent_id=agent_id)
            return True
        except APIError as e:
            if e.status_code == 404:
                return False
            raise
    
    # User and Credits Management
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info and credits.
        
        Returns:
            Dictionary containing user information including:
                - id (str): User identifier
                - email (str): User email
                - credits (int): Remaining credits
                - plan (str): Current subscription plan
        
        Raises:
            AuthenticationError: If API key is invalid
            APIError: If request fails
        
        Example:
            >>> client = AISpine(api_key="sk_your_api_key")
            >>> user = client.get_current_user()
            >>> print(f"User: {user['email']}, Credits: {user['credits']}")
        """
        return self._request("GET", "/api/v1/users/me")
    
    def check_user_api_key(self, user_id: str) -> Dict[str, Any]:
        """Check if a user has an API key generated.
        
        Note: This endpoint does not require authentication.
        
        Args:
            user_id: Supabase Auth user ID
            
        Returns:
            Dictionary containing:
                - has_api_key (bool): Whether user has an API key
                - api_key (str|None): The API key if it exists
                - credits (int): Available credits
                - rate_limit (int): Rate limit for the user
                - created_at (str): When the key was created
                - last_used_at (str|None): Last usage timestamp
        
        Raises:
            ValidationError: If user_id is invalid
            APIError: If request fails
        
        Example:
            >>> client = AISpine(api_key="sk_any_key")  # API key not used for this endpoint
            >>> status = client.check_user_api_key("123e4567-e89b-12d3-a456-426614174000")
            >>> if status["has_api_key"]:
            ...     print(f"User has API key: {status['api_key']}")
        """
        if not user_id:
            raise ValidationError("User ID is required")
        
        return self._request(
            "GET",
            "/api/v1/user/keys/my-key",
            params={"user_id": user_id},
            auth_required=False
        )
    
    def generate_user_api_key(self, user_id: str) -> Dict[str, Any]:
        """Generate or regenerate API key for a user.
        
        Note: This endpoint does not require authentication.
        
        Args:
            user_id: Supabase Auth user ID
            
        Returns:
            Dictionary containing:
                - message (str): Success message
                - api_key (str): The generated API key
                - action (str): "created" or "regenerated"
        
        Raises:
            ValidationError: If user_id is invalid
            APIError: If request fails
        
        Example:
            >>> client = AISpine(api_key="sk_any_key")  # API key not used for this endpoint
            >>> result = client.generate_user_api_key("123e4567-e89b-12d3-a456-426614174000")
            >>> print(f"API Key {result['action']}: {result['api_key']}")
        """
        if not user_id:
            raise ValidationError("User ID is required")
        
        return self._request(
            "POST",
            "/api/v1/user/keys/generate",
            data={"user_id": user_id},
            auth_required=False
        )
    
    def revoke_user_api_key(self, user_id: str) -> Dict[str, Any]:
        """Revoke (delete) a user's API key.
        
        Note: This endpoint does not require authentication.
        
        Args:
            user_id: Supabase Auth user ID
            
        Returns:
            Dictionary containing:
                - message (str): Success message
                - status (str): "revoked"
        
        Raises:
            ValidationError: If user_id is invalid
            APIError: If request fails
        
        Example:
            >>> client = AISpine(api_key="sk_any_key")  # API key not used for this endpoint
            >>> result = client.revoke_user_api_key("123e4567-e89b-12d3-a456-426614174000")
            >>> print(result['message'])
        """
        if not user_id:
            raise ValidationError("User ID is required")
        
        return self._request(
            "DELETE",
            "/api/v1/user/keys/revoke",
            data={"user_id": user_id},
            auth_required=False
        )
    
    def check_credits(self) -> int:
        """Check remaining credits before making expensive calls.
        
        Returns:
            Number of remaining credits
        
        Raises:
            AuthenticationError: If API key is invalid
            APIError: If request fails
        
        Example:
            >>> client = AISpine(api_key="sk_your_api_key")
            >>> credits = client.check_credits()
            >>> if credits < 10:
            ...     print("Low on credits!")
        """
        user = self.get_current_user()
        return user.get("credits", 0)
    
    # System Operations
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status.
        
        Returns:
            Health status dictionary
        """
        return self._request("GET", ENDPOINTS["health"])
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics.
        
        Returns:
            Metrics dictionary
        """
        return self._request("GET", ENDPOINTS["metrics"])
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status.
        
        Returns:
            Status dictionary
        """
        return self._request("GET", ENDPOINTS["status"])
    
    # Convenience Methods
    
    def execute_and_wait(
        self,
        flow_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_EXECUTION_TIMEOUT,
        interval: int = DEFAULT_POLLING_INTERVAL
    ) -> Dict[str, Any]:
        """Execute a flow and wait for completion.
        
        Args:
            flow_id: Unique flow identifier
            input_data: Input data for flow execution
            metadata: Optional metadata
            timeout: Maximum wait time in seconds
            interval: Polling interval in seconds
            
        Returns:
            Final execution result
            
        Raises:
            ValidationError: If inputs are invalid
            TimeoutError: If execution doesn't complete in time
            ExecutionError: If execution fails
        """
        execution = self.execute_flow(flow_id, input_data, metadata)
        execution_id = execution["execution_id"]
        
        return self.wait_for_execution(execution_id, timeout, interval)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()