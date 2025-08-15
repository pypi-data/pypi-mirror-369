"""Example of API key management using AI Spine SDK.

Note: The API key management endpoints do not require authentication.
The API key passed to the client is not used for these operations.
"""

import os
import sys
from typing import Optional

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_spine import AISpine
from ai_spine.exceptions import ValidationError, APIError


def manage_user_api_key(client: AISpine, user_id: str) -> None:
    """Demonstrate API key management operations.
    
    Note: These operations do not require authentication.
    
    Args:
        client: AISpine client instance (API key not used for these operations)
        user_id: Supabase Auth user ID
    """
    print(f"\n=== API Key Management for User: {user_id} ===")
    print("Note: These endpoints do not require authentication\n")
    
    try:
        # Check if user has an API key
        print("1. Checking for existing API key...")
        status = client.check_user_api_key(user_id)
        
        if status["has_api_key"]:
            print(f"   ✓ User has API key: {status['api_key'][:10]}...")
            print(f"   - Credits: {status['credits']}")
            print(f"   - Rate limit: {status['rate_limit']}")
            print(f"   - Created at: {status['created_at']}")
            if status.get('last_used_at'):
                print(f"   - Last used: {status['last_used_at']}")
        else:
            print("   ✗ User does not have an API key")
            
            # Generate API key for the first time
            print("\n2. Generating new API key...")
            result = client.generate_user_api_key(user_id)
            print(f"   ✓ API Key {result['action']}: {result['api_key']}")
            print(f"   - Message: {result['message']}")
            
            # Check status again
            print("\n3. Verifying API key was created...")
            status = client.check_user_api_key(user_id)
            if status["has_api_key"]:
                print(f"   ✓ Confirmed: API key exists")
        
        # Example: Regenerate API key (if compromised)
        print("\n4. Regenerating API key (simulating key rotation)...")
        regenerate_result = client.generate_user_api_key(user_id)
        print(f"   ✓ API Key {regenerate_result['action']}: {regenerate_result['api_key']}")
        print(f"   - This invalidates the previous key")
        
        # Example: Revoke API key
        user_input = input("\n5. Do you want to revoke this API key? (y/N): ")
        if user_input.lower() == 'y':
            print("   Revoking API key...")
            revoke_result = client.revoke_user_api_key(user_id)
            print(f"   ✓ {revoke_result['message']}")
            print(f"   - Status: {revoke_result['status']}")
            
            # Verify revocation
            print("\n6. Verifying API key was revoked...")
            final_status = client.check_user_api_key(user_id)
            if not final_status["has_api_key"]:
                print("   ✓ Confirmed: API key has been revoked")
        else:
            print("   Skipping API key revocation")
            
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    except APIError as e:
        print(f"❌ API error: {e}")
        if hasattr(e, 'details'):
            print(f"   Details: {e.details}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main function to run API key management examples."""
    # Note: API key is not required for these endpoints, but the client needs one
    # You can use any valid API key format (it won't be validated for these calls)
    api_key = "sk_placeholder"  # Not actually used for authentication
    
    # Get user ID from environment or prompt
    user_id = os.getenv("TEST_USER_ID")
    if not user_id:
        user_id = input("Enter the Supabase Auth user ID to manage: ").strip()
    
    print("\n📌 Important: The API key management endpoints do not require authentication.")
    print("   The client requires an API key parameter, but it won't be used for these calls.\n")
    
    # Initialize client
    client = AISpine(
        api_key=api_key,
        base_url="https://ai-spine-api.up.railway.app",  # Updated base URL
        debug=True  # Enable debug logging
    )
    
    try:
        # Run API key management demonstration
        manage_user_api_key(client, user_id)
        
    finally:
        # Clean up
        client.close()
        print("\n=== Example completed ===")


if __name__ == "__main__":
    main()