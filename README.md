# Jetpack 🚀

Project utilities to kickstart microservice development with Python and FastAPI.

## Overview

Jetpack provides essential building blocks for microservice development, including configuration management, structured logging, error handling, and standardized response schemas.

## Features

- **Configuration Management**: Environment-based settings with validation
- **Structured Logging**: Correlation ID tracking and configurable handlers
- **Error Handling**: Custom exceptions with FastAPI integration
- **Response Schemas**: Standardized API response formats
- **Type Safety**: Full type hints and Pydantic validation

## Installation

```bash
pip install jetpack
```

For FastAPI integration:
```bash
pip install jetpack[apis]
```

## Quick Start

### Configuration

```python
from jetpack.config import LogConfig, PathConf

# Access configuration
print(f"Log level: {LogConfig.LOG_LEVEL}")
print(f"Logs path: {PathConf.LOGS_MODULE_PATH}")
```

Set environment variables:
```bash
export LOG_LEVEL=DEBUG
export ENABLE_FILE_LOG=true
export MODULE_NAME=my-service
```

### Logging

```python
from jetpack.log_config import configure_logger

# Set up structured logging with correlation IDs
logger = configure_logger("my-service")

logger.info("Service started")
logger.error("Something went wrong", extra={"user_id": 123})
```

### Error Handling

```python
from jetpack.errors import GenericErrors
from jetpack.errors.exception_handlers import get_exception_handlers
from fastapi import FastAPI

# Custom exception
class ValidationError(GenericErrors):
    def __init__(self, message: str):
        super().__init__(message=message, ec="VAL_001", status_code=422)

# FastAPI setup
app = FastAPI()

# Add exception handlers
exception_handlers = get_exception_handlers([ValidationError])

# Use in your code
raise ValidationError("Invalid email format")
```

### Response Schemas

```python
from jetpack.responses import DefaultResponseSchema, DefaultFailureSchema

# Success response
response = DefaultResponseSchema(
    message="User created successfully",
    data={"user_id": 123, "username": "john_doe"}
)

# Error response
error_response = DefaultFailureSchema(
    message="Validation failed",
    error={"field": "email", "code": "INVALID_FORMAT"}
)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `ENABLE_FILE_LOG` | Enable file logging | `false` |
| `ENABLE_CONSOLE_LOG` | Enable console logging | `true` |
| `MODULE_NAME` | Service name for logs | `""` |
| `BASE_PATH` | Base path for data/logs | `code/data` |

## API Reference

### Configuration
- `LogConfig` - Logging configuration settings
- `PathConf` - Path and directory configuration

### Logging
- `configure_logger(project_name)` - Set up structured logging
- `read_configuration(project_name)` - Get logging configuration

### Error Handling
- `GenericErrors` - Base exception class
- `get_exception_handlers()` - FastAPI exception handlers

### Response Schemas
- `DefaultResponseSchema` - Success response format
- `DefaultFailureSchema` - Error response format
- `RequestMeta` - Request metadata with correlation IDs

## Examples

### Complete FastAPI Service

```python
from fastapi import FastAPI
from jetpack.log_config import configure_logger
from jetpack.responses import DefaultResponseSchema
from jetpack.errors import GenericErrors
from jetpack.errors.exception_handlers import get_exception_handlers

# Set up logging
logger = configure_logger("user-service")

# Create FastAPI app
app = FastAPI(title="User Service")

# Add exception handlers
app.add_exception_handler(Exception, get_exception_handlers())

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info(f"Fetching user {user_id}")

    # Your business logic here
    user_data = {"id": user_id, "name": "John Doe"}

    return DefaultResponseSchema(
        message="User retrieved successfully",
        data=user_data
    )

@app.post("/users")
async def create_user(user_data: dict):
    logger.info("Creating new user")

    # Validation logic
    if not user_data.get("email"):
        raise GenericErrors(
            message="Email is required",
            ec="USR_001",
            status_code=400
        )

    # Create user logic here
    new_user = {"id": 123, **user_data}

    return DefaultResponseSchema(
        message="User created successfully",
        data=new_user
    )
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/jetpack
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure 100% test coverage
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
