"""
Tests for jetpack.config module.
"""

import os
import pathlib
from unittest.mock import patch

import pytest

from jetpack.config import LogConfig, PathConf, _LogConfig, _PathConf, _BasePathConf


class TestLogConfig:
    """Test cases for LogConfig settings."""

    def test_default_values(self, clean_env):
        """Test that LogConfig has correct default values."""
        config = _LogConfig()

        assert config.LOG_LEVEL == "INFO"
        assert config.ENABLE_FILE_LOG is False
        assert config.ENABLE_CONSOLE_LOG is True
        assert config.LOG_ENABLE_TRACEBACK is False
        assert config.DEFER_LOG_MODULES == ["httpx", "pymongo"]
        assert config.DEFER_ADDITIONAL_LOGS == []
        assert config.DEFER_LOG_LEVEL == "INFO"

    def test_environment_variable_override(self, mock_env_vars):
        """Test that environment variables override default values."""
        config = _LogConfig()

        assert config.LOG_LEVEL == "DEBUG"
        assert config.ENABLE_FILE_LOG is True
        assert config.ENABLE_CONSOLE_LOG is False
        assert config.LOG_ENABLE_TRACEBACK is True
        assert config.DEFER_LOG_LEVEL == "WARNING"

    def test_singleton_instance(self):
        """Test that LogConfig is a singleton instance."""
        assert LogConfig is not None
        assert isinstance(LogConfig, _LogConfig)

    @pytest.mark.parametrize(
        "log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    def test_valid_log_levels(self, log_level):
        """Test that various log levels are accepted."""
        with patch.dict(os.environ, {"LOG_LEVEL": log_level}):
            config = _LogConfig()
            assert config.LOG_LEVEL == log_level

    @pytest.mark.parametrize(
        "boolean_value,expected",
        [
            ("true", True),
            ("false", False),
            ("True", True),
            ("False", False),
            ("1", True),
            ("0", False),
            ("yes", True),
            ("no", False),
        ],
    )
    def test_boolean_environment_values(self, boolean_value, expected):
        """Test that boolean environment variables are correctly parsed."""
        with patch.dict(os.environ, {"ENABLE_FILE_LOG": boolean_value}):
            config = _LogConfig()
            assert config.ENABLE_FILE_LOG is expected

    def test_defer_modules_as_list(self):
        """Test that DEFER_LOG_MODULES uses default list."""
        # Since BaseSettings doesn't automatically parse comma-separated strings to lists,
        # this test verifies the default behavior
        config = _LogConfig()
        # The field should have a default list value
        assert isinstance(config.DEFER_LOG_MODULES, list)
        assert "httpx" in config.DEFER_LOG_MODULES
        assert "pymongo" in config.DEFER_LOG_MODULES


class TestBasePathConf:
    """Test cases for BasePathConf settings."""

    def test_default_base_path(self, clean_env):
        """Test that BasePathConf has correct default BASE_PATH."""
        config = _BasePathConf()
        assert config.BASE_PATH == "code/data"

    def test_custom_base_path(self):
        """Test that BASE_PATH can be overridden by environment variable."""
        with patch.dict(os.environ, {"BASE_PATH": "/custom/path"}):
            config = _BasePathConf()
            assert config.BASE_PATH == "/custom/path"


class TestPathConf:
    """Test cases for PathConf settings."""

    def test_default_values(self, clean_env):
        """Test that PathConf has correct default values."""
        with patch.dict(os.environ, {"MODULE_NAME": "test-app"}):
            config = _PathConf()

            assert isinstance(config.BASE_PATH, pathlib.Path)
            assert str(config.BASE_PATH) == "code/data"
            assert config.MODULE_NAME == "test-app"
            assert config.LOGS_MODULE_PATH is not None

    def test_logs_module_path_construction(self):
        """Test that LOGS_MODULE_PATH is correctly constructed."""
        with patch.dict(
            os.environ, {"BASE_PATH": "/tmp/test", "MODULE_NAME": "my-service"}
        ):
            config = _PathConf()

            expected_path = os.path.join("/tmp/test", "logs", "my_service")
            assert str(config.LOGS_MODULE_PATH) == expected_path

    def test_module_name_hyphen_replacement(self):
        """Test that hyphens in MODULE_NAME are replaced with underscores in path."""
        with patch.dict(
            os.environ, {"BASE_PATH": "/test", "MODULE_NAME": "test-api-service"}
        ):
            config = _PathConf()

            expected_path = os.path.join("/test", "logs", "test_api_service")
            assert str(config.LOGS_MODULE_PATH) == expected_path

    def test_empty_module_name(self):
        """Test behavior with empty MODULE_NAME."""
        with patch.dict(os.environ, {"MODULE_NAME": ""}):
            config = _PathConf()

            # os.path.join with empty string at the end doesn't add trailing slash
            expected_path = "code/data/logs"
            assert str(config.LOGS_MODULE_PATH) == expected_path

    def test_singleton_instance(self):
        """Test that PathConf is a singleton instance."""
        assert PathConf is not None
        assert isinstance(PathConf, _PathConf)

    def test_path_merger_validator(self):
        """Test the path_merger model validator."""
        values = {"BASE_PATH": "/custom/base", "MODULE_NAME": "test-service"}

        result = _PathConf.path_merger(values)

        expected_logs_path = os.path.join("/custom/base", "logs", "test_service")
        assert result["LOGS_MODULE_PATH"] == expected_logs_path

    def test_pathlib_path_type(self):
        """Test that BASE_PATH is properly converted to pathlib.Path."""
        with patch.dict(os.environ, {"BASE_PATH": "/test/path"}):
            config = _PathConf()

            assert isinstance(config.BASE_PATH, pathlib.Path)
            assert str(config.BASE_PATH) == "/test/path"


class TestConfigExports:
    """Test that the module exports are correct."""

    def test_exports_available(self):
        """Test that LogConfig and PathConf are available as exports."""
        from jetpack.config import LogConfig, PathConf

        assert LogConfig is not None
        assert PathConf is not None

    def test_all_exports(self):
        """Test that __all__ contains the expected exports."""
        from jetpack import config

        assert hasattr(config, "__all__")
        assert "LogConfig" in config.__all__
        assert "PathConf" in config.__all__
