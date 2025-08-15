#!/usr/bin/env python3
"""
Example: Simple Authentication

This example demonstrates the basic usage of Keymaster HJY for API key
authentication, including key creation, validation, and error handling.

Prerequisites:
- Keymaster HJY installed: pip install keymaster_hjy
- Database configured in mysql.env file

Usage:
- python examples/basic/simple_auth.py
"""

import sys
from pathlib import Path

# Add the package to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from keymaster_hjy import master
from keymaster_hjy.exceptions import (
    InvalidKeyError,
    KeyExpiredError,
    RateLimitExceededError,
    ScopeDeniedError
)


def create_api_key():
    """Create a new API key for testing."""
    print("🔑 Creating a new API key...")
    
    try:
        key_info = master.keys.create(
            description="Simple authentication example",
            tags=["example", "demo"],
            scopes=["read:data", "write:data"]
        )
        
        print(f"✅ API key created successfully!")
        print(f"   ID: {key_info['id']}")
        print(f"   Key: {key_info['key']}")
        print(f"   🔒 Store this key securely!")
        
        return key_info['key']
        
    except Exception as e:
        print(f"❌ Failed to create API key: {e}")
        return None


def validate_api_key(api_key, required_scope=None):
    """Validate an API key with optional scope checking."""
    print(f"\n🔍 Validating API key: {api_key[:10]}...")
    
    try:
        master.auth.validate_key(
            api_key,
            required_scope=required_scope,
            source_ip="127.0.0.1",
            request_method="GET",
            request_path="/api/example"
        )
        
        scope_msg = f" with scope '{required_scope}'" if required_scope else ""
        print(f"✅ API key is valid{scope_msg}")
        return True
        
    except InvalidKeyError as e:
        print(f"❌ Invalid API key: {e}")
        print(f"💡 Suggestions: {'; '.join(e.suggestions)}")
        return False
        
    except KeyExpiredError as e:
        print(f"❌ API key expired: {e}")
        print(f"💡 Suggestions: {'; '.join(e.suggestions)}")
        return False
        
    except RateLimitExceededError as e:
        print(f"❌ Rate limit exceeded: {e}")
        print(f"💡 Suggestions: {'; '.join(e.suggestions)}")
        return False
        
    except ScopeDeniedError as e:
        print(f"❌ Insufficient permissions: {e}")
        print(f"💡 Suggestions: {'; '.join(e.suggestions)}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def demonstrate_scope_checking(api_key):
    """Demonstrate scope-based access control."""
    print("\n🎯 Demonstrating scope-based access control...")
    
    # Test with allowed scope
    print("\n1. Testing with allowed scope 'read:data':")
    validate_api_key(api_key, required_scope="read:data")
    
    # Test with another allowed scope
    print("\n2. Testing with allowed scope 'write:data':")
    validate_api_key(api_key, required_scope="write:data")
    
    # Test with denied scope
    print("\n3. Testing with denied scope 'admin:delete':")
    validate_api_key(api_key, required_scope="admin:delete")


def demonstrate_error_handling():
    """Demonstrate various error scenarios."""
    print("\n🚨 Demonstrating error handling...")
    
    # Test with invalid key
    print("\n1. Testing with invalid API key:")
    validate_api_key("invalid-key-format")
    
    # Test with malformed key
    print("\n2. Testing with malformed API key:")
    validate_api_key("lingchongtong-invalid-hash")


def main():
    """Main demonstration function."""
    print("🔐 Keymaster HJY - Simple Authentication Example")
    print("=" * 55)
    
    # Step 1: Create an API key
    api_key = create_api_key()
    if not api_key:
        print("❌ Cannot continue without a valid API key")
        return
    
    # Step 2: Basic validation
    print("\n" + "=" * 55)
    print("📋 Basic API Key Validation")
    validate_api_key(api_key)
    
    # Step 3: Scope-based validation
    print("\n" + "=" * 55)
    print("🎯 Scope-Based Access Control")
    demonstrate_scope_checking(api_key)
    
    # Step 4: Error handling demonstration
    print("\n" + "=" * 55)
    print("🚨 Error Handling Demonstration")
    demonstrate_error_handling()
    
    # Step 5: Summary
    print("\n" + "=" * 55)
    print("🎉 Example completed successfully!")
    print("\n📚 Key Takeaways:")
    print("   • API keys are created with specific scopes")
    print("   • Validation includes scope checking")
    print("   • Errors provide actionable suggestions")
    print("   • All operations are logged for audit purposes")
    
    print("\n🚀 Next Steps:")
    print("   • Try the FastAPI example: examples/fastapi/complete_app.py")
    print("   • Explore advanced features: examples/advanced/")
    print("   • Check production patterns: examples/deployment/")


if __name__ == "__main__":
    main()
