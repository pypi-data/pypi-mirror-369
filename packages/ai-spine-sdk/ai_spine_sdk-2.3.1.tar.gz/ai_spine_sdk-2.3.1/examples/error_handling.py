"""Error handling examples for AI Spine SDK."""

from ai_spine import (
    Client,
    AISpineError,
    ValidationError,
    ExecutionError,
    TimeoutError,
    RateLimitError,
    AuthenticationError,
    InsufficientCreditsError,
)


def main():
    # Initialize client with API key
    client = Client(
        api_key="sk_your_api_key_here",
        debug=True  # Enable debug mode for more details
    )
    
    # Example 1: Handle validation errors
    print("Example 1: Handling validation errors")
    print("-" * 50)
    
    try:
        # This will raise a ValidationError
        client.execute_flow("", {"data": "test"})
    except ValidationError as e:
        print(f"Validation error caught: {e}")
        if e.details:
            print(f"Error details: {e.details}")
    
    # Example 2: Handle execution failures
    print("\nExample 2: Handling execution failures")
    print("-" * 50)
    
    try:
        # Execute a flow that might fail
        result = client.execute_and_wait(
            flow_id="complex-analysis",
            input_data={"invalid_field": "data"},
            timeout=60
        )
    except ExecutionError as e:
        print(f"Execution failed: {e}")
        print(f"Execution ID: {e.execution_id}")
        if e.details:
            print(f"Failure details: {e.details}")
    except TimeoutError as e:
        print(f"Execution timed out: {e}")
        print(f"Timeout value: {e.timeout} seconds")
    
    # Example 3: Handle rate limiting
    print("\nExample 3: Handling rate limits")
    print("-" * 50)
    
    import time
    
    for i in range(5):
        try:
            # Make rapid requests that might trigger rate limiting
            flows = client.list_flows()
            print(f"Request {i+1} successful")
        except RateLimitError as e:
            print(f"Rate limit hit: {e}")
            if e.retry_after:
                print(f"Retry after {e.retry_after} seconds")
                time.sleep(e.retry_after)
                # Retry the request
                flows = client.list_flows()
                print("Retry successful")
    
    # Example 4: Handle insufficient credits
    print("\nExample 4: Handling insufficient credits")
    print("-" * 50)
    
    try:
        # This might fail if user has no credits
        result = client.execute_flow(
            flow_id="expensive-flow",
            input_data={"data": "test"}
        )
    except InsufficientCreditsError as e:
        print(f"Insufficient credits: {e}")
        if e.credits_needed:
            print(f"Credits needed: {e.credits_needed}")
        if e.credits_available is not None:
            print(f"Credits available: {e.credits_available}")
        print("Top up at https://ai-spine.com/billing")
    
    # Example 5: Handle authentication errors
    print("\nExample 5: Handling authentication errors")
    print("-" * 50)
    
    # Create client with invalid API key
    auth_client = Client(api_key="invalid-key")
    
    try:
        auth_client.list_flows()
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Get your API key from https://ai-spine.com/dashboard")
    
    # Example 6: Generic error handling
    print("\nExample 6: Generic error handling with retry")
    print("-" * 50)
    
    def execute_with_retry(client, flow_id, input_data, max_retries=3):
        """Execute flow with automatic retry on failure."""
        for attempt in range(max_retries):
            try:
                return client.execute_and_wait(flow_id, input_data)
            except AISpineError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if isinstance(e, (ValidationError, AuthenticationError)):
                    # Don't retry on validation or auth errors
                    raise
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries exceeded")
                    raise
    
    try:
        result = execute_with_retry(
            client,
            "test-flow",
            {"data": "test"}
        )
        print(f"Success: {result}")
    except AISpineError as e:
        print(f"Final failure: {e}")
    
    # Example 7: Context manager for automatic cleanup
    print("\nExample 7: Using context manager")
    print("-" * 50)
    
    try:
        with Client(api_key="sk_your_api_key_here") as context_client:
            # Client will automatically close even if error occurs
            result = context_client.health_check()
            print(f"Health check: {result}")
            
            # Simulate an error
            raise ValueError("Something went wrong")
    except ValueError as e:
        print(f"Error occurred: {e}")
        print("But client session was properly closed")
    
    # Clean up
    client.close()
    auth_client.close()


if __name__ == "__main__":
    main()