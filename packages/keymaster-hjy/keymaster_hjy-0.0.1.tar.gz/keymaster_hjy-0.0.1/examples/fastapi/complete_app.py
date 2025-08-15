#!/usr/bin/env python3
"""
Example: Complete FastAPI Application with Keymaster HJY

This example demonstrates a production-ready FastAPI application with
comprehensive API key authentication, rate limiting, and error handling.

Prerequisites:
- pip install keymaster_hjy[fastapi]
- Database configured in mysql.env file

Usage:
- python examples/fastapi/complete_app.py
- Open http://127.0.0.1:8000/docs for interactive API documentation
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add the package to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, Request, Depends, status
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ FastAPI dependencies not installed")
    print("📦 Install with: pip install keymaster_hjy[fastapi]")
    sys.exit(1)

from keymaster_hjy.integrations import fastapi_guard
from keymaster_hjy.exceptions import KeymasterError
from keymaster_hjy import master


# Pydantic models for request/response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class CreateUserRequest(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class ApiKeyResponse(BaseModel):
    id: int
    key: str
    description: str
    scopes: List[str]


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


# Create FastAPI app with comprehensive configuration
app = FastAPI(
    title="Secure API with Keymaster HJY",
    description="Production-ready API with comprehensive authentication and rate limiting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for Keymaster errors
@app.exception_handler(KeymasterError)
async def keymaster_exception_handler(request: Request, exc: KeymasterError):
    """Global handler for all Keymaster authentication errors."""
    
    # Map error types to HTTP status codes
    status_map = {
        "INVALID_KEY": status.HTTP_401_UNAUTHORIZED,
        "KEY_DEACTIVATED": status.HTTP_401_UNAUTHORIZED,
        "KEY_EXPIRED": status.HTTP_401_UNAUTHORIZED,
        "SCOPE_DENIED": status.HTTP_403_FORBIDDEN,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "INIT_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "CONFIG_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_map.get(exc.error_code, status.HTTP_400_BAD_REQUEST)
    
    # Add Retry-After header for rate limiting
    headers = {}
    if exc.error_code == "RATE_LIMIT_EXCEEDED":
        retry_after = exc.details.get("reset_time", 60)
        headers["Retry-After"] = str(retry_after)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.error_code,
            "message": str(exc).split(" | Suggestions:")[0],
            "details": exc.details,
            "suggestions": exc.suggestions,
            "timestamp": datetime.now().isoformat()
        },
        headers=headers
    )


# Health check endpoint (no authentication required)
@app.get("/health", response_model=ApiResponse, tags=["System"])
async def health_check():
    """Health check endpoint for monitoring systems."""
    return ApiResponse(
        success=True,
        data={"status": "healthy", "timestamp": datetime.now().isoformat()},
        message="Service is running normally"
    )


# Public information endpoint (requires valid API key)
@app.get("/api/info", response_model=ApiResponse, tags=["Public"])
async def get_public_info(request: Request, _: None = Depends(fastapi_guard())):
    """Get public API information. Requires a valid API key."""
    return ApiResponse(
        success=True,
        data={
            "api_name": "Secure API with Keymaster HJY",
            "version": "1.0.0",
            "features": ["Authentication", "Rate Limiting", "Audit Logging"],
            "client_ip": request.client.host,
            "timestamp": datetime.now().isoformat()
        },
        message="Public information retrieved successfully"
    )


# User endpoints with scope-based permissions
@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(_: None = Depends(fastapi_guard("read:users"))):
    """List all users. Requires 'read:users' scope."""
    # Mock user data
    users = [
        UserResponse(
            id=1,
            username="alice",
            email="alice@example.com",
            created_at=datetime.now()
        ),
        UserResponse(
            id=2,
            username="bob",
            email="bob@example.com",
            created_at=datetime.now()
        )
    ]
    return users


@app.post("/api/users", response_model=UserResponse, tags=["Users"])
async def create_user(
    user_data: CreateUserRequest,
    _: None = Depends(fastapi_guard("write:users"))
):
    """Create a new user. Requires 'write:users' scope."""
    # Mock user creation
    new_user = UserResponse(
        id=999,
        username=user_data.username,
        email=user_data.email,
        created_at=datetime.now()
    )
    return new_user


@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: int,
    _: None = Depends(fastapi_guard("read:users"))
):
    """Get a specific user by ID. Requires 'read:users' scope."""
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be positive"
        )
    
    # Mock user data
    return UserResponse(
        id=user_id,
        username=f"user_{user_id}",
        email=f"user_{user_id}@example.com",
        created_at=datetime.now()
    )


# Admin endpoints with strict permissions
@app.get("/api/admin/stats", response_model=ApiResponse, tags=["Admin"])
async def get_admin_stats(_: None = Depends(fastapi_guard("admin:read"))):
    """Get system statistics. Requires 'admin:read' scope."""
    return ApiResponse(
        success=True,
        data={
            "total_users": 1000,
            "active_keys": 50,
            "requests_today": 25000,
            "uptime": "99.9%"
        },
        message="Admin statistics retrieved successfully"
    )


@app.post("/api/admin/maintenance", response_model=ApiResponse, tags=["Admin"])
async def trigger_maintenance(_: None = Depends(fastapi_guard("admin:write"))):
    """Trigger maintenance mode. Requires 'admin:write' scope."""
    return ApiResponse(
        success=True,
        data={"maintenance_started": True},
        message="Maintenance mode activated"
    )


# API key management endpoints
@app.post("/api/keys", response_model=ApiKeyResponse, tags=["API Keys"])
async def create_api_key(
    description: str,
    scopes: List[str],
    _: None = Depends(fastapi_guard("manage:keys"))
):
    """Create a new API key. Requires 'manage:keys' scope."""
    try:
        key_info = master.keys.create(
            description=description,
            scopes=scopes,
            tags=["api-created"]
        )
        
        return ApiKeyResponse(
            id=key_info['id'],
            key=key_info['key'],
            description=description,
            scopes=scopes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


# Rate limiting demonstration endpoint
@app.get("/api/rate-limit-test", response_model=ApiResponse, tags=["Testing"])
async def rate_limit_test(_: None = Depends(fastapi_guard())):
    """
    Test rate limiting. Make multiple requests quickly to see rate limiting in action.
    Default limit is 100 requests per minute.
    """
    return ApiResponse(
        success=True,
        data={
            "message": "Rate limit test successful",
            "timestamp": datetime.now().isoformat(),
            "tip": "Make many requests quickly to test rate limiting"
        }
    )


# Error demonstration endpoints
@app.get("/api/demo/invalid-scope", tags=["Demo"])
async def demo_invalid_scope(_: None = Depends(fastapi_guard("nonexistent:scope"))):
    """Demonstrate scope denial error. This will fail unless you have 'nonexistent:scope'."""
    return {"message": "You have the required scope!"}


@app.get("/api/demo/server-error", tags=["Demo"])
async def demo_server_error():
    """Demonstrate server error handling."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="This is a demo server error"
    )


def setup_demo_data():
    """Set up demo API keys for testing."""
    print("🔧 Setting up demo data...")
    
    try:
        # Create demo keys with different permission levels
        demo_keys = [
            {
                "description": "Demo read-only key",
                "scopes": ["read:users"],
                "tags": ["demo", "readonly"]
            },
            {
                "description": "Demo read-write key", 
                "scopes": ["read:users", "write:users"],
                "tags": ["demo", "readwrite"]
            },
            {
                "description": "Demo admin key",
                "scopes": ["read:users", "write:users", "admin:read", "admin:write", "manage:keys"],
                "tags": ["demo", "admin"]
            }
        ]
        
        created_keys = []
        for key_config in demo_keys:
            key_info = master.keys.create(**key_config)
            created_keys.append(key_info)
            print(f"   ✅ Created {key_config['description']}: {key_info['key']}")
        
        print(f"\n🎯 Demo keys created! Use them to test the API:")
        print(f"   📖 Read-only key:  {created_keys[0]['key']}")
        print(f"   ✏️  Read-write key: {created_keys[1]['key']}")
        print(f"   👑 Admin key:      {created_keys[2]['key']}")
        
        return created_keys
        
    except Exception as e:
        print(f"   ⚠️  Could not create demo keys: {e}")
        print(f"   💡 You can create keys manually or use existing ones")
        return []


def main():
    """Main function to run the FastAPI application."""
    print("🚀 Starting Secure FastAPI Application with Keymaster HJY")
    print("=" * 65)
    
    # Set up demo data
    demo_keys = setup_demo_data()
    
    print(f"\n📚 API Documentation:")
    print(f"   🌐 Interactive docs: http://127.0.0.1:8000/docs")
    print(f"   📖 ReDoc docs:       http://127.0.0.1:8000/redoc")
    print(f"   🔧 Health check:     http://127.0.0.1:8000/health")
    
    print(f"\n🧪 Testing Examples:")
    if demo_keys:
        admin_key = demo_keys[2]['key']
        print(f"   # Test with admin key:")
        print(f"   curl -H 'X-API-Key: {admin_key}' http://127.0.0.1:8000/api/users")
        print(f"   curl -H 'X-API-Key: {admin_key}' http://127.0.0.1:8000/api/admin/stats")
    else:
        print(f"   # Test with your API key:")
        print(f"   curl -H 'X-API-Key: YOUR_KEY_HERE' http://127.0.0.1:8000/api/info")
    
    print(f"\n🎯 Available Endpoints:")
    print(f"   GET  /health                 - Health check (no auth)")
    print(f"   GET  /api/info               - Public info (any valid key)")
    print(f"   GET  /api/users              - List users (read:users)")
    print(f"   POST /api/users              - Create user (write:users)")
    print(f"   GET  /api/users/{{id}}         - Get user (read:users)")
    print(f"   GET  /api/admin/stats        - Admin stats (admin:read)")
    print(f"   POST /api/admin/maintenance  - Maintenance (admin:write)")
    print(f"   POST /api/keys               - Create key (manage:keys)")
    print(f"   GET  /api/rate-limit-test    - Test rate limiting")
    
    print(f"\n🔥 Starting server...")
    
    # Run the application
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
