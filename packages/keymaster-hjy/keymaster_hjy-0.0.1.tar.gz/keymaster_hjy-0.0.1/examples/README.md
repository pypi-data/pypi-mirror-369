# Keymaster HJY Examples

This directory contains comprehensive examples showing how to use Keymaster HJY in various scenarios and frameworks.

## 📁 Directory Structure

```
examples/
├── basic/                 # Basic usage examples
├── fastapi/              # FastAPI integration examples
├── flask/                # Flask integration examples
├── advanced/             # Advanced features and patterns
├── deployment/           # Production deployment examples
└── troubleshooting/      # Common issues and solutions
```

## 🚀 Quick Start Examples

### Basic Usage
- [`basic/simple_auth.py`](basic/simple_auth.py) - Basic API key creation and validation
- [`basic/key_management.py`](basic/key_management.py) - Complete key lifecycle management
- [`basic/scopes_demo.py`](basic/scopes_demo.py) - Permission scopes demonstration

### Framework Integration
- [`fastapi/complete_app.py`](fastapi/complete_app.py) - Full FastAPI application with authentication
- [`fastapi/async_patterns.py`](fastapi/async_patterns.py) - Async/await patterns and best practices
- [`flask/complete_app.py`](flask/complete_app.py) - Full Flask application with authentication
- [`flask/blueprints.py`](flask/blueprints.py) - Using Keymaster with Flask blueprints

### Advanced Features
- [`advanced/rate_limiting.py`](advanced/rate_limiting.py) - Custom rate limiting strategies
- [`advanced/key_rotation.py`](advanced/key_rotation.py) - Automatic key rotation patterns
- [`advanced/multi_tenant.py`](advanced/multi_tenant.py) - Multi-tenant API security
- [`advanced/audit_logging.py`](advanced/audit_logging.py) - Advanced audit logging and monitoring

### Production Deployment
- [`deployment/docker/`](deployment/docker/) - Docker containerization examples
- [`deployment/kubernetes/`](deployment/kubernetes/) - Kubernetes deployment manifests
- [`deployment/monitoring/`](deployment/monitoring/) - Monitoring and alerting setup

## 🔧 Running the Examples

### Prerequisites
```bash
# Install Keymaster HJY with all dependencies
pip install keymaster_hjy[all]

# Set up your environment
cp .env.example mysql.env
# Edit mysql.env with your database credentials
```

### Running Individual Examples
```bash
# Basic examples
python examples/basic/simple_auth.py

# Framework examples
python examples/fastapi/complete_app.py
python examples/flask/complete_app.py

# Advanced examples
python examples/advanced/rate_limiting.py
```

## 📚 Example Categories

### 🎯 **Beginner-Friendly**
Perfect for getting started with Keymaster HJY:
- Basic key creation and validation
- Simple framework integration
- Common use cases and patterns

### 🔧 **Production-Ready**
Real-world patterns for production deployments:
- Error handling and recovery
- Performance optimization
- Security best practices
- Monitoring and logging

### 🚀 **Advanced Techniques**
Advanced features and custom implementations:
- Custom rate limiting algorithms
- Multi-tenant architectures
- Integration with external systems
- Performance tuning and scaling

## 🆘 Getting Help

If you need help with any example:

1. **Check the comments** - Each example is thoroughly documented
2. **Review the troubleshooting guide** - [`troubleshooting/common_issues.md`](troubleshooting/common_issues.md)
3. **Open an issue** - [GitHub Issues](https://github.com/hjy/keymaster_hjy/issues)
4. **Read the main docs** - [Main Documentation](../README.md)

## 🤝 Contributing Examples

We welcome contributions! To add a new example:

1. Choose the appropriate directory
2. Follow the existing naming conventions
3. Include comprehensive comments and documentation
4. Add error handling and best practices
5. Update this README with your example

## 📝 Example Template

When creating new examples, use this template:

```python
#!/usr/bin/env python3
"""
Example: [Brief Description]

This example demonstrates [what it shows].

Prerequisites:
- [list requirements]

Usage:
- [how to run]
"""

# Your example code here
```
