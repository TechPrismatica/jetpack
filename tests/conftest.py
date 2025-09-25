"""
Pytest configuration and fixtures for jetpack tests.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "ENABLE_FILE_LOG": "true",
        "ENABLE_CONSOLE_LOG": "false",
        "LOG_ENABLE_TRACEBACK": "true",
        "BASE_PATH": "/tmp/test_data",
        "MODULE_NAME": "test-module",
        "DEFER_LOG_LEVEL": "WARNING",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def clean_env():
    """Fixture to clean environment variables for isolated testing."""
    original_env = os.environ.copy()
    # Clear jetpack-related env vars
    env_keys_to_clear = [
        "LOG_LEVEL",
        "ENABLE_FILE_LOG",
        "ENABLE_CONSOLE_LOG",
        "LOG_ENABLE_TRACEBACK",
        "BASE_PATH",
        "MODULE_NAME",
        "DEFER_LOG_LEVEL",
    ]
    for key in env_keys_to_clear:
        os.environ.pop(key, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_log_config():
    """Sample logging configuration for testing."""
    return {
        "name": "test-app",
        "handlers": [
            {
                "type": "RotatingFileHandler",
                "max_bytes": 1000000,
                "back_up_count": 3,
                "enable": True,
            },
            {"type": "StreamHandler", "enable": True},
        ],
    }
