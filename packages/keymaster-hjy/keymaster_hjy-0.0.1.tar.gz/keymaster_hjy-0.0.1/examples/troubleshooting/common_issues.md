# Troubleshooting Common Issues

This guide helps you diagnose and resolve common issues when using Keymaster HJY.

## 🚨 Common Error Scenarios

### 1. Initialization Errors

#### `InitializationError: Cannot find mysql.env file`

**Symptoms:**
```
InitializationError: Cannot find mysql.env file (Details: missing_config=mysql.env) | 
Suggestions: Check that mysql.env file exists in your project root; Verify database connection parameters; Run 'keymaster init' for interactive setup
```

**Solutions:**
1. **Create mysql.env file:**
   ```bash
   # Run interactive setup
   keymaster init
   
   # Or create manually
   cat > mysql.env << EOF
   MYSQL_HOST=your-host
   MYSQL_PORT=3306
   MYSQL_USER=your-user
   MYSQL_PASSWORD=your-password
   MYSQL_DATABASE=your-database
   EOF
   ```

2. **Check file location:**
   ```bash
   # Ensure mysql.env is in your project root
   ls -la mysql.env
   ```

3. **Verify file permissions:**
   ```bash
   chmod 600 mysql.env  # Secure permissions
   ```

#### `DatabaseError: Connection timeout`

**Symptoms:**
```
DatabaseError: Database operation failed: connection (Details: operation=connection, original_error=Connection timeout)
```

**Solutions:**
1. **Check database connectivity:**
   ```bash
   # Test MySQL connection
   mysql -h your-host -P 3306 -u your-user -p your-database
   ```

2. **Verify network access:**
   ```bash
   # Test port connectivity
   telnet your-host 3306
   nc -zv your-host 3306
   ```

3. **Check credentials:**
   ```python
   # Test connection with Python
   import mysql.connector
   
   connection = mysql.connector.connect(
       host='your-host',
       port=3306,
       user='your-user',
       password='your-password',
       database='your-database'
   )
   print("✅ Connection successful")
   connection.close()
   ```

### 2. Authentication Errors

#### `InvalidKeyError: Invalid API key provided`

**Symptoms:**
```
InvalidKeyError: Invalid API key provided (key: abc***xyz): Key not found in database
```

**Solutions:**
1. **Verify key format:**
   ```python
   # Keys should follow the pattern: prefix-hash
   # Example: lingchongtong-abc123def456
   ```

2. **Check key exists:**
   ```python
   from keymaster_hjy import master
   
   # Create a new key if needed
   key_info = master.keys.create(description="Test key")
   print(f"New key: {key_info['key']}")
   ```

3. **Verify key is active:**
   ```python
   # Keys might be deactivated
   try:
       master.auth.validate_key("your-key")
   except KeyDeactivatedError:
       print("Key is deactivated - create a new one")
   ```

#### `ScopeDeniedError: Missing required scope`

**Symptoms:**
```
ScopeDeniedError: Missing required scope: 'admin:write' (available: read:users, write:posts)
```

**Solutions:**
1. **Check required vs available scopes:**
   ```python
   # Create key with required scopes
   key_info = master.keys.create(
       description="Admin key",
       scopes=["admin:write", "admin:read"]  # Add required scopes
   )
   ```

2. **Use correct scope names:**
   ```python
   # Common scope patterns:
   # read:resource, write:resource, admin:action
   # Examples: read:users, write:posts, admin:delete
   ```

#### `RateLimitExceededError: Rate limit exceeded`

**Symptoms:**
```
RateLimitExceededError: Rate limit exceeded (150/minute > 100/minute) | 
Suggestions: Retry after 45 seconds; Reduce request frequency or implement backoff
```

**Solutions:**
1. **Implement retry with backoff:**
   ```python
   import time
   from keymaster_hjy.exceptions import RateLimitExceededError
   
   def api_call_with_retry(api_key, max_retries=3):
       for attempt in range(max_retries):
           try:
               master.auth.validate_key(api_key)
               return True
           except RateLimitExceededError as e:
               if attempt == max_retries - 1:
                   raise
               wait_time = e.details.get("reset_time", 60)
               time.sleep(wait_time)
   ```

2. **Increase rate limits:**
   ```python
   # Create key with higher limit
   key_info = master.keys.create(
       description="High frequency key",
       rate_limit="1000/minute"
   )
   ```

3. **Implement request queuing:**
   ```python
   import asyncio
   from asyncio import Queue
   
   async def rate_limited_processor(queue: Queue, api_key: str):
       while True:
           request = await queue.get()
           try:
               master.auth.validate_key(api_key)
               # Process request
               queue.task_done()
           except RateLimitExceededError as e:
               # Re-queue and wait
               await queue.put(request)
               await asyncio.sleep(e.details.get("reset_time", 60))
   ```

### 3. Configuration Issues

#### `ConfigurationError: Invalid configuration`

**Symptoms:**
```
ConfigurationError: Invalid configuration for 'MYSQL_PORT': not-a-number (expected: integer between 1-65535)
```

**Solutions:**
1. **Fix configuration values:**
   ```bash
   # mysql.env
   MYSQL_HOST=localhost          # ✅ Valid hostname/IP
   MYSQL_PORT=3306              # ✅ Valid port number
   MYSQL_USER=myuser            # ✅ Valid username
   MYSQL_PASSWORD=mypass        # ✅ Valid password
   MYSQL_DATABASE=mydb          # ✅ Valid database name
   ```

2. **Validate configuration:**
   ```python
   from keymaster_hjy.config_provider import ConfigProvider
   
   config = ConfigProvider().get_mysql_config()
   print("Configuration loaded successfully:", config)
   ```

### 4. Redis Connection Issues

#### Redis not available (falls back to memory limiting)

**Symptoms:**
```
Warning: Redis not available, using in-memory rate limiting
```

**Solutions:**
1. **Install Redis:**
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   
   # macOS
   brew install redis
   
   # Start Redis
   redis-server
   ```

2. **Configure Redis in mysql.env:**
   ```bash
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your-redis-password  # if required
   ```

3. **Test Redis connection:**
   ```python
   import redis
   
   r = redis.Redis(host='localhost', port=6379)
   r.ping()  # Should return True
   ```

## 🔧 Debugging Tips

### Enable Debug Logging

```python
import logging

# Enable debug logging for Keymaster
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('keymaster_hjy')
logger.setLevel(logging.DEBUG)
```

### Check Database Tables

```sql
-- Verify tables were created
SHOW TABLES LIKE 'keymaster_%';

-- Check key data
SELECT id, description, is_active, created_at FROM keymaster_keys;

-- Check settings
SELECT * FROM keymaster_settings;

-- Check recent logs
SELECT * FROM keymaster_logs ORDER BY timestamp DESC LIMIT 10;
```

### Test Database Connection

```python
from keymaster_hjy.config_provider import ConfigProvider
from keymaster_hjy.db_init import build_mysql_url
from sqlalchemy import create_engine

# Test database connection
config = ConfigProvider().get_mysql_config()
url = build_mysql_url(config)
engine = create_engine(url)

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("✅ Database connection successful")
```

### Verify API Key Creation

```python
from keymaster_hjy import master

# Create and immediately test a key
key_info = master.keys.create(description="Debug test key")
print(f"Created key: {key_info}")

# Test the key immediately
try:
    master.auth.validate_key(key_info['key'])
    print("✅ Key validation successful")
except Exception as e:
    print(f"❌ Key validation failed: {e}")
```

## 🚀 Performance Issues

### Slow Database Operations

1. **Check database indexes:**
   ```sql
   SHOW INDEX FROM keymaster_keys;
   SHOW INDEX FROM keymaster_logs;
   ```

2. **Monitor query performance:**
   ```sql
   -- Enable slow query log
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 1;
   ```

3. **Optimize connection pooling:**
   ```python
   from sqlalchemy import create_engine
   
   # Configure connection pool
   engine = create_engine(
       url,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

### Memory Issues

1. **Monitor memory usage:**
   ```python
   import psutil
   
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

2. **Configure Redis memory limits:**
   ```bash
   # redis.conf
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   ```

## 📞 Getting Help

### Information to Gather

When reporting issues, please include:

1. **Error message and stack trace**
2. **Keymaster HJY version:** `pip show keymaster_hjy`
3. **Python version:** `python --version`
4. **Database type and version**
5. **Configuration (without sensitive data)**
6. **Steps to reproduce**

### Diagnostic Script

```python
#!/usr/bin/env python3
"""Keymaster HJY Diagnostic Script"""

import sys
from pathlib import Path

def run_diagnostics():
    print("🔍 Keymaster HJY Diagnostics")
    print("=" * 40)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check package installation
    try:
        import keymaster_hjy
        print(f"✅ Keymaster HJY installed")
    except ImportError:
        print(f"❌ Keymaster HJY not installed")
        return
    
    # Check configuration file
    mysql_env = Path("mysql.env")
    if mysql_env.exists():
        print(f"✅ mysql.env found")
    else:
        print(f"❌ mysql.env not found")
        return
    
    # Test configuration loading
    try:
        from keymaster_hjy.config_provider import ConfigProvider
        config = ConfigProvider().get_mysql_config()
        print(f"✅ Configuration loaded")
        print(f"   Host: {config.get('host')}")
        print(f"   Database: {config.get('database')}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Test database connection
    try:
        from keymaster_hjy import master
        # This will test database connection
        print(f"✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    print(f"\n🎉 All diagnostics passed!")

if __name__ == "__main__":
    run_diagnostics()
```

### Community Resources

- **GitHub Issues:** [Report bugs and issues](https://github.com/hjy/keymaster_hjy/issues)
- **Documentation:** [Main documentation](../../README.md)
- **Examples:** [More examples](../)

## 🔄 Quick Fixes Checklist

- [ ] mysql.env file exists and has correct permissions
- [ ] Database server is running and accessible
- [ ] Database credentials are correct
- [ ] Required database tables exist
- [ ] API keys are properly formatted
- [ ] Scopes match what's required
- [ ] Rate limits are appropriate for usage
- [ ] Redis is configured if using distributed rate limiting
- [ ] Python dependencies are installed
- [ ] No firewall blocking database connections
