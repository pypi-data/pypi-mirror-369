#!/usr/bin/env python3
"""
Example: Complete Key Lifecycle Management

This example demonstrates the full lifecycle of API keys in Keymaster HJY,
including creation, validation, rotation, and deactivation.

Prerequisites:
- Keymaster HJY installed: pip install keymaster_hjy
- Database configured in mysql.env file

Usage:
- python examples/basic/key_management.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the package to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from keymaster_hjy import master
from keymaster_hjy.exceptions import KeymasterError


def create_key_with_options():
    """Create API keys with various configuration options."""
    print("🔑 Creating API keys with different configurations...")
    
    keys = []
    
    try:
        # Basic key
        print("\n1. Creating basic API key:")
        basic_key = master.keys.create(
            description="Basic API key for testing"
        )
        keys.append(basic_key)
        print(f"   ✅ Basic key created: {basic_key['key'][:20]}...")
        
        # Key with custom rate limit
        print("\n2. Creating key with custom rate limit:")
        rate_limited_key = master.keys.create(
            description="High-frequency API key",
            rate_limit="500/minute"  # Higher than default
        )
        keys.append(rate_limited_key)
        print(f"   ✅ Rate-limited key created: {rate_limited_key['key'][:20]}...")
        
        # Key with specific scopes
        print("\n3. Creating key with specific scopes:")
        scoped_key = master.keys.create(
            description="Read-only API key",
            scopes=["read:users", "read:posts", "read:comments"]
        )
        keys.append(scoped_key)
        print(f"   ✅ Scoped key created: {scoped_key['key'][:20]}...")
        
        # Key with expiration
        print("\n4. Creating key with expiration:")
        expiration = (datetime.now() + timedelta(hours=24)).isoformat()
        expiring_key = master.keys.create(
            description="Temporary API key (24h)",
            expires_at=expiration
        )
        keys.append(expiring_key)
        print(f"   ✅ Expiring key created: {expiring_key['key'][:20]}...")
        print(f"      Expires: {expiration}")
        
        # Key with tags for organization
        print("\n5. Creating key with organization tags:")
        tagged_key = master.keys.create(
            description="Mobile app production key",
            tags=["mobile", "production", "v2.1"],
            scopes=["read:users", "write:analytics"]
        )
        keys.append(tagged_key)
        print(f"   ✅ Tagged key created: {tagged_key['key'][:20]}...")
        print(f"      Tags: {', '.join(['mobile', 'production', 'v2.1'])}")
        
        return keys
        
    except Exception as e:
        print(f"❌ Failed to create keys: {e}")
        return []


def demonstrate_key_rotation(key_id):
    """Demonstrate key rotation with transition period."""
    print(f"\n🔄 Demonstrating key rotation for key ID: {key_id}")
    
    try:
        # Rotate the key with a 1-hour transition period
        print("   Rotating key with 1-hour transition period...")
        new_key_info = master.keys.rotate(
            key_id=key_id,
            transition_period_hours=1
        )
        
        print(f"   ✅ Key rotated successfully!")
        print(f"      New key ID: {new_key_info['id']}")
        print(f"      New key: {new_key_info['key'][:20]}...")
        print(f"      Old key remains valid for 1 hour")
        
        return new_key_info
        
    except Exception as e:
        print(f"   ❌ Key rotation failed: {e}")
        return None


def demonstrate_key_deactivation(key_id):
    """Demonstrate key deactivation."""
    print(f"\n🚫 Demonstrating key deactivation for key ID: {key_id}")
    
    try:
        master.keys.deactivate(key_id)
        print(f"   ✅ Key {key_id} deactivated successfully")
        print(f"      The key is now permanently disabled")
        
    except Exception as e:
        print(f"   ❌ Key deactivation failed: {e}")


def test_key_validation(api_key, description):
    """Test key validation and show the results."""
    print(f"\n🔍 Testing {description}:")
    print(f"   Key: {api_key[:20]}...")
    
    try:
        master.auth.validate_key(api_key)
        print(f"   ✅ Key is valid and active")
        return True
        
    except KeymasterError as e:
        print(f"   ❌ Validation failed: {e.error_code}")
        print(f"      Message: {str(e).split(' | Suggestions:')[0]}")
        return False


def demonstrate_key_lifecycle():
    """Demonstrate the complete key lifecycle."""
    print("🔄 Demonstrating complete key lifecycle...")
    
    # Create a key for lifecycle demo
    try:
        key_info = master.keys.create(
            description="Lifecycle demonstration key",
            tags=["demo", "lifecycle"]
        )
        key_id = key_info['id']
        api_key = key_info['key']
        
        print(f"\n1. ✅ Key created (ID: {key_id})")
        
        # Test the new key
        print(f"\n2. Testing newly created key:")
        test_key_validation(api_key, "newly created key")
        
        # Rotate the key
        print(f"\n3. Rotating the key:")
        new_key_info = demonstrate_key_rotation(key_id)
        
        if new_key_info:
            new_api_key = new_key_info['key']
            
            # Test both keys during transition period
            print(f"\n4. Testing keys during transition period:")
            test_key_validation(api_key, "original key (should still work)")
            test_key_validation(new_api_key, "new key (should work)")
            
            # Deactivate the new key for demo
            print(f"\n5. Deactivating the new key:")
            demonstrate_key_deactivation(new_key_info['id'])
            
            # Test the deactivated key
            print(f"\n6. Testing deactivated key:")
            test_key_validation(new_api_key, "deactivated key")
    
    except Exception as e:
        print(f"❌ Lifecycle demonstration failed: {e}")


def show_key_management_best_practices():
    """Show best practices for key management."""
    print("\n📚 Key Management Best Practices:")
    print("\n🔒 Security:")
    print("   • Store keys securely (environment variables, key vaults)")
    print("   • Use specific scopes - grant minimum required permissions")
    print("   • Set expiration dates for temporary access")
    print("   • Rotate keys regularly in production")
    
    print("\n🏷️ Organization:")
    print("   • Use descriptive names for keys")
    print("   • Tag keys by environment, service, or purpose")
    print("   • Document key purposes and owners")
    
    print("\n📊 Monitoring:")
    print("   • Monitor key usage patterns")
    print("   • Set up alerts for unusual activity")
    print("   • Review and audit key access regularly")
    print("   • Deactivate unused keys promptly")
    
    print("\n🔄 Lifecycle Management:")
    print("   • Plan key rotation schedules")
    print("   • Use transition periods for zero-downtime rotation")
    print("   • Test key changes in staging environments")
    print("   • Have key recovery procedures documented")


def main():
    """Main demonstration function."""
    print("🔐 Keymaster HJY - Complete Key Management Example")
    print("=" * 60)
    
    # Step 1: Create various types of keys
    print("📋 Step 1: Creating Keys with Different Configurations")
    keys = create_key_with_options()
    
    if not keys:
        print("❌ Cannot continue without keys")
        return
    
    # Step 2: Demonstrate key lifecycle
    print("\n" + "=" * 60)
    print("🔄 Step 2: Key Lifecycle Management")
    demonstrate_key_lifecycle()
    
    # Step 3: Show best practices
    print("\n" + "=" * 60)
    print("📚 Step 3: Best Practices")
    show_key_management_best_practices()
    
    # Step 4: Cleanup (deactivate demo keys)
    print("\n" + "=" * 60)
    print("🧹 Step 4: Cleanup (Deactivating Demo Keys)")
    
    for key_info in keys[:2]:  # Only deactivate first 2 keys as examples
        try:
            master.keys.deactivate(key_info['id'])
            print(f"   ✅ Deactivated key {key_info['id']}")
        except Exception as e:
            print(f"   ❌ Failed to deactivate key {key_info['id']}: {e}")
    
    print(f"\n   💡 Note: {len(keys) - 2} keys left active for further testing")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Key Management Example Completed!")
    print("\n🚀 Next Steps:")
    print("   • Try scope-based examples: examples/basic/scopes_demo.py")
    print("   • Explore advanced rotation: examples/advanced/key_rotation.py")
    print("   • Check production patterns: examples/deployment/")


if __name__ == "__main__":
    main()
