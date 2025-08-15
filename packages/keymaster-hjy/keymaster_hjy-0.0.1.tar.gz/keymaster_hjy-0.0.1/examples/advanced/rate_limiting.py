#!/usr/bin/env python3
"""
Example: Advanced Rate Limiting Patterns

This example demonstrates advanced rate limiting techniques with Keymaster HJY,
including custom limits, burst handling, and rate limit monitoring.

Prerequisites:
- pip install keymaster_hjy
- Redis configured for distributed rate limiting (optional)
- Database configured in mysql.env file

Usage:
- python examples/advanced/rate_limiting.py
"""

import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Add the package to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from keymaster_hjy import master
from keymaster_hjy.exceptions import RateLimitExceededError, KeymasterError


class RateLimitMonitor:
    """Monitor and track rate limiting behavior."""
    
    def __init__(self):
        self.requests = []
        self.rate_limits = []
    
    def record_request(self, success: bool, error_code: str = None, reset_time: int = None):
        """Record a request attempt."""
        self.requests.append({
            "timestamp": datetime.now(),
            "success": success,
            "error_code": error_code,
            "reset_time": reset_time
        })
    
    def record_rate_limit(self, current_rate: str, limit: str, reset_time: int):
        """Record rate limit information."""
        self.rate_limits.append({
            "timestamp": datetime.now(),
            "current_rate": current_rate,
            "limit": limit,
            "reset_time": reset_time
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about rate limiting."""
        total_requests = len(self.requests)
        successful_requests = sum(1 for r in self.requests if r["success"])
        rate_limited = sum(1 for r in self.requests if r["error_code"] == "RATE_LIMIT_EXCEEDED")
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "rate_limited_requests": rate_limited,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "rate_limit_events": len(self.rate_limits)
        }


def create_keys_with_different_limits():
    """Create API keys with different rate limits for testing."""
    print("🔑 Creating API keys with different rate limits...")
    
    keys = []
    
    try:
        # Low limit key for quick testing
        low_limit_key = master.keys.create(
            description="Low limit key (5/minute)",
            rate_limit="5/minute",
            tags=["demo", "low-limit"]
        )
        keys.append(("low", low_limit_key))
        print(f"   ✅ Low limit key: {low_limit_key['key'][:20]}... (5/minute)")
        
        # Medium limit key
        medium_limit_key = master.keys.create(
            description="Medium limit key (30/minute)",
            rate_limit="30/minute",
            tags=["demo", "medium-limit"]
        )
        keys.append(("medium", medium_limit_key))
        print(f"   ✅ Medium limit key: {medium_limit_key['key'][:20]}... (30/minute)")
        
        # High limit key
        high_limit_key = master.keys.create(
            description="High limit key (100/minute)",
            rate_limit="100/minute",
            tags=["demo", "high-limit"]
        )
        keys.append(("high", high_limit_key))
        print(f"   ✅ High limit key: {high_limit_key['key'][:20]}... (100/minute)")
        
        # Burst limit key (high per-second limit)
        burst_limit_key = master.keys.create(
            description="Burst limit key (10/second)",
            rate_limit="10/second",
            tags=["demo", "burst-limit"]
        )
        keys.append(("burst", burst_limit_key))
        print(f"   ✅ Burst limit key: {burst_limit_key['key'][:20]}... (10/second)")
        
        return keys
        
    except Exception as e:
        print(f"❌ Failed to create keys: {e}")
        return []


def test_rate_limit_single_key(api_key: str, limit_type: str, num_requests: int = 10):
    """Test rate limiting behavior with a single key."""
    print(f"\n🧪 Testing rate limiting: {limit_type} limit ({num_requests} requests)")
    
    monitor = RateLimitMonitor()
    
    for i in range(num_requests):
        try:
            # Make request with some context
            master.auth.validate_key(
                api_key,
                request_id=f"test-{i+1}",
                source_ip="127.0.0.1",
                request_method="GET",
                request_path="/api/test"
            )
            
            monitor.record_request(success=True)
            print(f"   ✅ Request {i+1}: Success")
            
        except RateLimitExceededError as e:
            monitor.record_rate_limit(
                e.details.get("current_rate", "unknown"),
                e.details.get("limit", "unknown"),
                e.details.get("reset_time", 60)
            )
            monitor.record_request(
                success=False,
                error_code="RATE_LIMIT_EXCEEDED",
                reset_time=e.details.get("reset_time")
            )
            print(f"   ❌ Request {i+1}: Rate limited ({e.details.get('current_rate')} > {e.details.get('limit')})")
            
        except Exception as e:
            monitor.record_request(success=False, error_code=type(e).__name__)
            print(f"   ❌ Request {i+1}: Error - {e}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    # Show statistics
    stats = monitor.get_stats()
    print(f"\n📊 Rate Limiting Statistics for {limit_type}:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Successful: {stats['successful_requests']}")
    print(f"   Rate limited: {stats['rate_limited_requests']}")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    
    return monitor


def test_burst_behavior(api_key: str, burst_size: int = 15):
    """Test burst behavior - many requests in quick succession."""
    print(f"\n💥 Testing burst behavior: {burst_size} rapid requests")
    
    monitor = RateLimitMonitor()
    start_time = time.time()
    
    for i in range(burst_size):
        try:
            master.auth.validate_key(
                api_key,
                request_id=f"burst-{i+1}",
                source_ip="127.0.0.1"
            )
            
            monitor.record_request(success=True)
            elapsed = time.time() - start_time
            print(f"   ✅ Burst request {i+1}: Success (t+{elapsed:.3f}s)")
            
        except RateLimitExceededError as e:
            monitor.record_request(
                success=False,
                error_code="RATE_LIMIT_EXCEEDED"
            )
            elapsed = time.time() - start_time
            reset_time = e.details.get("reset_time", 60)
            print(f"   ❌ Burst request {i+1}: Rate limited (t+{elapsed:.3f}s, retry in {reset_time}s)")
            
        except Exception as e:
            monitor.record_request(success=False)
            print(f"   ❌ Burst request {i+1}: Error - {e}")
    
    total_time = time.time() - start_time
    stats = monitor.get_stats()
    
    print(f"\n📊 Burst Test Results:")
    print(f"   Total time: {total_time:.3f} seconds")
    print(f"   Requests/second: {burst_size / total_time:.2f}")
    print(f"   Successful requests: {stats['successful_requests']}/{burst_size}")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    
    return monitor


def test_concurrent_requests(api_key: str, num_threads: int = 5, requests_per_thread: int = 3):
    """Test rate limiting under concurrent load."""
    print(f"\n🔀 Testing concurrent requests: {num_threads} threads × {requests_per_thread} requests")
    
    def make_requests(thread_id: int):
        """Make requests from a single thread."""
        results = []
        
        for i in range(requests_per_thread):
            try:
                master.auth.validate_key(
                    api_key,
                    request_id=f"thread-{thread_id}-req-{i+1}",
                    source_ip="127.0.0.1"
                )
                results.append(("success", None))
                
            except RateLimitExceededError as e:
                results.append(("rate_limited", e.details.get("reset_time", 60)))
                
            except Exception as e:
                results.append(("error", str(e)))
            
            time.sleep(0.05)  # Small delay between requests
        
        return thread_id, results
    
    # Execute concurrent requests
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(make_requests, i) for i in range(num_threads)]
        all_results = [future.result() for future in futures]
    
    total_time = time.time() - start_time
    
    # Analyze results
    total_requests = 0
    successful_requests = 0
    rate_limited_requests = 0
    error_requests = 0
    
    for thread_id, results in all_results:
        for result_type, _ in results:
            total_requests += 1
            if result_type == "success":
                successful_requests += 1
            elif result_type == "rate_limited":
                rate_limited_requests += 1
            else:
                error_requests += 1
        
        print(f"   Thread {thread_id}: {len([r for r in results if r[0] == 'success'])}/{len(results)} successful")
    
    print(f"\n📊 Concurrent Test Results:")
    print(f"   Total time: {total_time:.3f} seconds")
    print(f"   Total requests: {total_requests}")
    print(f"   Successful: {successful_requests}")
    print(f"   Rate limited: {rate_limited_requests}")
    print(f"   Errors: {error_requests}")
    print(f"   Success rate: {successful_requests/total_requests:.2%}")
    print(f"   Requests/second: {total_requests/total_time:.2f}")


def demonstrate_rate_limit_recovery(api_key: str):
    """Demonstrate recovery after hitting rate limits."""
    print(f"\n🔄 Demonstrating rate limit recovery...")
    
    # First, hit the rate limit
    print("   Step 1: Hitting rate limit...")
    
    for i in range(10):  # Try to exceed limit
        try:
            master.auth.validate_key(api_key)
            print(f"      ✅ Request {i+1}: Success")
        except RateLimitExceededError as e:
            reset_time = e.details.get("reset_time", 60)
            print(f"      ❌ Request {i+1}: Rate limited (reset in {reset_time}s)")
            
            # Wait for rate limit to reset
            if reset_time <= 5:  # Only wait if it's a short reset time
                print(f"   Step 2: Waiting {reset_time} seconds for reset...")
                time.sleep(reset_time + 1)  # Add 1 second buffer
                
                # Try again after reset
                print("   Step 3: Testing after reset...")
                try:
                    master.auth.validate_key(api_key)
                    print("      ✅ Request after reset: Success")
                    return
                except Exception as e:
                    print(f"      ❌ Request after reset: {e}")
            else:
                print(f"   ⏱️  Reset time too long ({reset_time}s), skipping wait")
            
            break
        except Exception as e:
            print(f"      ❌ Request {i+1}: Error - {e}")
            break


def show_rate_limiting_best_practices():
    """Show best practices for handling rate limits."""
    print("\n📚 Rate Limiting Best Practices:")
    
    print("\n🔧 Application Design:")
    print("   • Implement exponential backoff for retries")
    print("   • Use request queuing to smooth traffic bursts")
    print("   • Cache responses when possible to reduce API calls")
    print("   • Monitor rate limit headers in responses")
    
    print("\n📊 Monitoring & Alerting:")
    print("   • Track rate limit hit rates")
    print("   • Alert on unusual rate limiting patterns")
    print("   • Monitor API usage trends")
    print("   • Set up dashboards for rate limit metrics")
    
    print("\n⚙️ Configuration:")
    print("   • Set appropriate limits based on usage patterns")
    print("   • Use different limits for different API key tiers")
    print("   • Consider time-based limits (daily, hourly, per-minute)")
    print("   • Plan for burst traffic scenarios")
    
    print("\n🔄 Error Handling:")
    print("   • Parse rate limit error details")
    print("   • Respect retry-after times")
    print("   • Implement circuit breakers for failing services")
    print("   • Provide meaningful error messages to users")


def main():
    """Main demonstration function."""
    print("🚀 Keymaster HJY - Advanced Rate Limiting Patterns")
    print("=" * 60)
    
    # Step 1: Create keys with different limits
    print("📋 Step 1: Creating Test Keys")
    keys = create_keys_with_different_limits()
    
    if not keys:
        print("❌ Cannot continue without test keys")
        return
    
    # Step 2: Test individual key limits
    print("\n" + "=" * 60)
    print("🧪 Step 2: Testing Individual Rate Limits")
    
    # Test with low limit key (should hit limit quickly)
    low_limit_key = next(key_info for limit_type, key_info in keys if limit_type == "low")
    test_rate_limit_single_key(low_limit_key['key'], "low", num_requests=8)
    
    # Step 3: Test burst behavior
    print("\n" + "=" * 60)
    print("💥 Step 3: Testing Burst Behavior")
    
    burst_key = next(key_info for limit_type, key_info in keys if limit_type == "burst")
    test_burst_behavior(burst_key['key'], burst_size=15)
    
    # Step 4: Test concurrent requests
    print("\n" + "=" * 60)
    print("🔀 Step 4: Testing Concurrent Requests")
    
    medium_key = next(key_info for limit_type, key_info in keys if limit_type == "medium")
    test_concurrent_requests(medium_key['key'], num_threads=3, requests_per_thread=4)
    
    # Step 5: Demonstrate recovery
    print("\n" + "=" * 60)
    print("🔄 Step 5: Rate Limit Recovery")
    
    demonstrate_rate_limit_recovery(low_limit_key['key'])
    
    # Step 6: Best practices
    print("\n" + "=" * 60)
    print("📚 Step 6: Best Practices")
    show_rate_limiting_best_practices()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Advanced Rate Limiting Demo Complete!")
    
    print("\n🚀 Next Steps:")
    print("   • Try the FastAPI example: examples/fastapi/complete_app.py")
    print("   • Explore key rotation: examples/advanced/key_rotation.py")
    print("   • Check monitoring patterns: examples/deployment/monitoring/")


if __name__ == "__main__":
    main()
