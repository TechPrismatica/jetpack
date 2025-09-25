# GitHub Copilot Instructions for Jetpack

## Project Overview

Jetpack is a Python utility library for microservice development, providing configuration management, structured logging, error handling, and response schemas. The codebase emphasizes type safety, clean architecture, and comprehensive testing.

## Code Style & Patterns

### General Principles
- Use type hints for all functions and variables
- Follow PEP 8 style guidelines
- Prefer composition over inheritance
- Write self-documenting code with clear naming
- Maintain 100% test coverage

### Import Organization
```python
# Standard library imports
import os
import logging
from typing import Optional, Any

# Third-party imports
from pydantic import BaseModel, Field
from fastapi import Request, status

# Local imports
from jetpack.config import LogConfig
from jetpack.errors import GenericErrors
```

### Type Hints
Always use type hints:
```python
def configure_logger(project_name: str = PathConf.MODULE_NAME) -> logging.Logger:
    """Configure logger with correlation ID support."""
    pass

class RequestMeta(BaseModel):
    request_id: Optional[str] = Field(default_factory=get_correlation_id)
    timestamp: Optional[str] = Field(default_factory=get_current_timestamp)
```

## Architecture Patterns

### Configuration Management
- Use Pydantic BaseSettings for environment-based configuration
- Provide sensible defaults
- Use model validators for complex field relationships
- Create singleton instances for global access

```python
class _LogConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    ENABLE_FILE_LOG: Optional[bool] = False

    @model_validator(mode="before")
    def validate_settings(cls, values):
        # Custom validation logic
        return values

LogConfig = _LogConfig()  # Singleton instance
```

### Error Handling
- Extend GenericErrors for custom exceptions
- Include error codes (ec) for categorization
- Set appropriate HTTP status codes
- Provide descriptive error messages

```python
class ValidationError(GenericErrors):
    def __init__(self, field: str, value: Any):
        super().__init__(
            message=f"Invalid value '{value}' for field '{field}'",
            ec="VAL_001",
            status_code=422
        )
```

### Response Schemas
- Use Pydantic models for response structure
- Include metadata with correlation IDs
- Separate success and failure schemas
- Provide factory functions when needed

```python
def success_response(data: Any, message: str = "Operation successful") -> DefaultResponseSchema:
    return DefaultResponseSchema(
        message=message,
        data=data,
        meta=RequestMeta()
    )
```

### Logging
- Use structured logging with correlation IDs
- Configure handlers based on environment
- Support both file and console output
- Defer logging for specific modules

```python
logger = configure_logger("service-name")
logger.info("Operation completed", extra={
    "user_id": user_id,
    "operation": "create_user"
})
```

## Testing Patterns

### Test Structure
- Use pytest with fixtures for setup
- Group tests in classes by functionality
- Use descriptive test names
- Test both success and failure cases

```python
class TestGenericErrors:
    def test_initialization_with_all_parameters(self):
        """Test GenericErrors with all parameters."""
        error = GenericErrors(
            message="Test error",
            ec="TEST_001",
            status_code=400
        )

        assert error.message == "TEST_001: Test error"
        assert error.status_code == 400
```

### Mocking
- Mock external dependencies
- Use fixtures for common test data
- Patch at the appropriate level
- Clean up after tests

```python
@pytest.fixture
def mock_correlation_id():
    with patch('jetpack.responses.correlation_id') as mock:
        mock.get.return_value = 'test-id-123'
        yield mock
```

### Coverage
- Maintain 100% test coverage
- Test edge cases and error conditions
- Use parametrized tests for multiple scenarios
- Mock ContextVars and external services properly

## File Organization

```
jetpack/
├── src/jetpack/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── log_config.py      # Logging setup
│   ├── responses.py       # Response schemas
│   └── errors/
│       ├── __init__.py    # Base exception classes
│       └── exception_handlers.py  # FastAPI handlers
└── tests/
    ├── conftest.py        # Shared fixtures
    ├── test_config.py
    ├── test_errors.py
    ├── test_exception_handlers.py
    ├── test_log_config.py
    └── test_responses.py
```

## Common Patterns to Suggest

### Configuration Access
```python
# Good - Use singleton instances
from jetpack.config import LogConfig, PathConf
log_level = LogConfig.LOG_LEVEL

# Avoid - Don't recreate instances
config = _LogConfig()  # ❌
```

### Exception Handling
```python
# Good - Specific exceptions with context
raise ValidationError(f"Invalid email format: {email}")

# Good - Generic with error code
raise GenericErrors(
    message="Database connection failed",
    ec="DB_001",
    status_code=503
)
```

### Response Creation
```python
# Good - Use schema classes
return DefaultResponseSchema(
    message="User created",
    data=user_dict,
    meta=RequestMeta()
)

# Avoid - Raw dictionaries
return {"status": "success", "data": user_dict}  # ❌
```

### Logging
```python
# Good - Structured logging with context
logger.info("User operation completed", extra={
    "user_id": user.id,
    "operation": "update_profile",
    "duration_ms": duration
})

# Avoid - String formatting in log messages
logger.info(f"User {user.id} updated")  # ❌
```

## Dependencies to Prefer

- **pydantic**: For data validation and settings
- **fastapi**: For API frameworks (optional dependency)
- **asgi-correlation-id**: For request tracing
- **whenever**: For timestamp handling
- **pytest**: For testing
- **coverage**: For test coverage

## When Adding New Features

1. **Add type hints** to all new functions
2. **Write tests first** (TDD approach)
3. **Update configuration** if new settings are needed
4. **Add proper error handling** with custom exceptions
5. **Include logging** for important operations
6. **Document in docstrings** with examples
7. **Maintain backwards compatibility** when possible

## Code Review Checklist

- [ ] Type hints present and accurate
- [ ] Tests written and passing (100% coverage)
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Configuration externalized
- [ ] Documentation updated
- [ ] Backwards compatibility maintained
- [ ] Performance considerations addressed
