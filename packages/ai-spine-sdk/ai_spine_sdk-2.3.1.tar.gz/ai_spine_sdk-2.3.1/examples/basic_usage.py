"""Basic usage example for AI Spine SDK."""

from ai_spine import Client


def main():
    # Initialize the client with your API key
    # Get your API key from https://ai-spine.com/dashboard
    client = Client(
        api_key="sk_your_api_key_here",  # Required - use your personal API key
        # base_url="https://custom-api.ai-spine.com"  # Optional - uses production by default
    )
    
    # Check your credits before making expensive calls
    try:
        credits = client.check_credits()
        print(f"Remaining credits: {credits}")
        if credits < 10:
            print("Warning: Low on credits! Top up at https://ai-spine.com/billing")
    except Exception as e:
        print(f"Error checking credits: {e}")
    
    # Example 1: Execute a flow and wait for completion
    print("Example 1: Execute and wait for flow completion")
    print("-" * 50)
    
    try:
        # Execute flow with input data
        result = client.execute_and_wait(
            flow_id="credit-analysis",
            input_data={
                "customer_id": "CUST-001",
                "loan_amount": 50000,
                "loan_term": 36,
                "purpose": "business_expansion"
            },
            timeout=300  # Wait up to 5 minutes
        )
        
        print(f"Execution completed!")
        print(f"Status: {result['status']}")
        if result.get('output_data'):
            print(f"Output: {result['output_data']}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Execute flow and poll manually
    print("\nExample 2: Execute flow with manual polling")
    print("-" * 50)
    
    try:
        # Start execution
        execution = client.execute_flow(
            flow_id="sentiment-analysis",
            input_data={
                "text": "This product exceeded my expectations! Highly recommended."
            }
        )
        
        print(f"Execution started: {execution['execution_id']}")
        
        # Poll for status
        import time
        while True:
            status = client.get_execution(execution['execution_id'])
            print(f"Current status: {status['status']}")
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                if status['status'] == 'completed':
                    print(f"Result: {status.get('output_data')}")
                else:
                    print(f"Execution failed: {status.get('error_message')}")
                break
            
            time.sleep(2)  # Wait 2 seconds before next poll
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: List available flows
    print("\nExample 3: List available flows")
    print("-" * 50)
    
    try:
        flows = client.list_flows()
        print(f"Found {len(flows)} flows:")
        for flow in flows:
            print(f"  - {flow.get('flow_id')}: {flow.get('name', 'Unnamed')}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Get current user info
    print("\nExample 4: Get current user info")
    print("-" * 50)
    
    try:
        user = client.get_current_user()
        print(f"User: {user.get('email', 'Unknown')}")
        print(f"Credits: {user.get('credits', 0)}")
        print(f"Plan: {user.get('plan', 'Unknown')}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Check system health
    print("\nExample 5: System health check")
    print("-" * 50)
    
    try:
        health = client.health_check()
        print(f"System status: {health.get('status')}")
        if health.get('version'):
            print(f"API version: {health['version']}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Clean up
    client.close()


if __name__ == "__main__":
    main()