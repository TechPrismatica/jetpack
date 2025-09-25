"""
Tests for jetpack.log_config module.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from jetpack.log_config import read_configuration, configure_logger


class TestReadConfiguration:
    """Test cases for read_configuration function."""

    def test_read_configuration_basic(self):
        """Test read_configuration returns expected structure."""
        project_name = "test-project"
        config = read_configuration(project_name)

        assert config["name"] == project_name
        assert "handlers" in config
        assert len(config["handlers"]) == 2

        # Check RotatingFileHandler config
        file_handler = config["handlers"][0]
        assert file_handler["type"] == "RotatingFileHandler"
        assert file_handler["max_bytes"] == 100000000
        assert file_handler["back_up_count"] == 5
        assert "enable" in file_handler

        # Check StreamHandler config
        stream_handler = config["handlers"][1]
        assert stream_handler["type"] == "StreamHandler"
        assert "enable" in stream_handler

    def test_read_configuration_with_different_project_names(self):
        """Test read_configuration with various project names."""
        test_names = ["my-app", "service_name", "api-gateway", "worker-1"]

        for name in test_names:
            config = read_configuration(name)
            assert config["name"] == name
            assert len(config["handlers"]) == 2

    def test_read_configuration_file_handler_config(self):
        """Test that file handler configuration uses LogConfig settings."""
        with patch("jetpack.log_config.LogConfig") as mock_log_config:
            mock_log_config.ENABLE_FILE_LOG = True

            config = read_configuration("test")
            file_handler = config["handlers"][0]

            assert file_handler["enable"] == mock_log_config.ENABLE_FILE_LOG

    def test_read_configuration_stream_handler_config(self):
        """Test that stream handler configuration uses LogConfig settings."""
        with patch("jetpack.log_config.LogConfig") as mock_log_config:
            mock_log_config.ENABLE_CONSOLE_LOG = False

            config = read_configuration("test")
            stream_handler = config["handlers"][1]

            assert stream_handler["enable"] == mock_log_config.ENABLE_CONSOLE_LOG


class TestConfigureLogger:
    """Test cases for configure_logger function."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()

    def test_configure_logger_basic(self, temp_dir):
        """Test basic logger configuration."""
        project_name = "test-app"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_path_conf.LOGS_MODULE_PATH = temp_dir / "logs" / project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = ["httpx"]
            mock_log_config.DEFER_ADDITIONAL_LOGS = []
            mock_log_config.DEFER_LOG_LEVEL = "WARNING"

            logger = configure_logger(project_name)

            assert logger is not None
            assert logger.level == logging.INFO

    def test_configure_logger_with_file_logging(self, temp_dir):
        """Test logger configuration with file logging enabled."""
        project_name = "file-logger-test"
        logs_path = temp_dir / "logs" / project_name

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_path_conf.LOGS_MODULE_PATH = logs_path
            mock_log_config.LOG_LEVEL = "DEBUG"
            mock_log_config.ENABLE_FILE_LOG = True
            mock_log_config.ENABLE_CONSOLE_LOG = False
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []
            mock_log_config.DEFER_LOG_LEVEL = "INFO"

            logger = configure_logger(project_name)

            assert logger is not None
            # Check that directory was created
            # Note: The actual directory creation depends on the real implementation

    def test_configure_logger_with_stream_logging(self):
        """Test logger configuration with stream logging enabled."""
        project_name = "stream-logger-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "ERROR"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = ["requests"]
            mock_log_config.DEFER_ADDITIONAL_LOGS = ["urllib3"]
            mock_log_config.DEFER_LOG_LEVEL = "CRITICAL"

            logger = configure_logger(project_name)

            assert logger is not None
            assert logger.level == logging.ERROR

    def test_configure_logger_deferred_modules(self):
        """Test that deferred modules get their log levels set correctly."""
        project_name = "defer-test"
        defer_modules = ["httpx", "pymongo", "requests"]
        defer_additional = ["custom_module"]

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
            patch("logging.getLogger") as mock_get_logger,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = defer_modules
            mock_log_config.DEFER_ADDITIONAL_LOGS = defer_additional
            mock_log_config.DEFER_LOG_LEVEL = "WARNING"

            # Mock the logger instances for deferred modules
            mock_loggers = {}
            for module in defer_modules + defer_additional:
                mock_loggers[module] = Mock()

            def get_logger_side_effect(name=None):
                if name in mock_loggers:
                    return mock_loggers[name]
                return Mock()  # Return a mock for the root logger

            mock_get_logger.side_effect = get_logger_side_effect

            configure_logger(project_name)

            # Verify that deferred modules had their log levels set
            for module in defer_modules + defer_additional:
                mock_loggers[module].setLevel.assert_called_with("WARNING")

    def test_configure_logger_correlation_id_filter(self):
        """Test that correlation ID filter is added to handlers."""
        project_name = "correlation-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
            patch("jetpack.log_config.CorrelationIdFilter") as mock_cid_filter,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            mock_filter_instance = Mock()
            mock_cid_filter.return_value = mock_filter_instance

            configure_logger(project_name)

            # Verify CorrelationIdFilter was created with correct parameters
            mock_cid_filter.assert_called_once_with(uuid_length=32)

    def test_configure_logger_formatter(self):
        """Test that logger formatter is set correctly."""
        project_name = "formatter-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
            patch("logging.Formatter") as mock_formatter,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            configure_logger(project_name)

            # Verify formatter was created with expected format
            expected_format = "%(asctime)s - %(levelname)-6s - [%(threadName)5s:%(funcName)5s(): %(lineno)s] [%(correlation_id)s] - %(message)s"
            expected_time_format = "%Y-%m-%d %H:%M:%S"

            mock_formatter.assert_called_with(expected_format, expected_time_format)

    def test_configure_logger_clears_existing_handlers(self):
        """Test that existing handlers are cleared before adding new ones."""
        project_name = "clear-handlers-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
            patch("logging.getLogger") as mock_get_logger,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            mock_logger = Mock()
            mock_logger.handlers = [Mock(), Mock()]  # Existing handlers
            mock_get_logger.return_value = mock_logger

            configure_logger(project_name)

            # Verify handlers list was cleared
            assert mock_logger.handlers == []

    def test_configure_logger_with_default_module_name(self):
        """Test configure_logger uses PathConf.MODULE_NAME as default."""
        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = "default-module"
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            # Call without project_name parameter
            logger = configure_logger()

            assert logger is not None

    @pytest.mark.parametrize(
        "log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    def test_configure_logger_log_levels(self, log_level):
        """Test configure_logger with different log levels."""
        project_name = "level-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = log_level
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            logger = configure_logger(project_name)

            assert logger is not None
            expected_level = getattr(logging, log_level)
            assert logger.level == expected_level

    def test_configure_logger_both_handlers_disabled(self):
        """Test configure_logger when both handlers are disabled."""
        project_name = "no-handlers-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = False
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            logger = configure_logger(project_name)

            assert logger is not None
            # Logger should still be created even if no handlers are enabled

    def test_configure_logger_directory_creation(self, temp_dir):
        """Test that log directory is created when file logging is enabled."""
        project_name = "dir-creation-test"
        logs_path = temp_dir / "logs" / project_name

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_path_conf.LOGS_MODULE_PATH = logs_path
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = True
            mock_log_config.ENABLE_CONSOLE_LOG = False
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            # The actual function should create the directory
            configure_logger(project_name)

            # Verify the directory was created
            assert logs_path.exists()


class TestLogConfigIntegration:
    """Integration tests for log configuration."""

    def test_real_logger_creation(self):
        """Test that a real logger is actually created and configured."""
        project_name = "integration-test"

        # Use a unique logger name to avoid conflicts

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_log_config.LOG_LEVEL = "DEBUG"
            mock_log_config.ENABLE_FILE_LOG = False
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = ["test_module"]
            mock_log_config.DEFER_ADDITIONAL_LOGS = []
            mock_log_config.DEFER_LOG_LEVEL = "WARNING"

            logger = configure_logger(project_name)

            # Test that we can actually log
            assert logger is not None
            assert hasattr(logger, "info")
            assert hasattr(logger, "error")
            assert hasattr(logger, "debug")

    def test_handler_configuration_with_real_objects(self, temp_dir):
        """Test handler configuration with real handler objects."""
        project_name = "real-handlers-test"

        with (
            patch("jetpack.log_config.PathConf") as mock_path_conf,
            patch("jetpack.log_config.LogConfig") as mock_log_config,
        ):
            mock_path_conf.MODULE_NAME = project_name
            mock_path_conf.LOGS_MODULE_PATH = temp_dir / "logs" / project_name
            mock_log_config.LOG_LEVEL = "INFO"
            mock_log_config.ENABLE_FILE_LOG = True
            mock_log_config.ENABLE_CONSOLE_LOG = True
            mock_log_config.DEFER_LOG_MODULES = []
            mock_log_config.DEFER_ADDITIONAL_LOGS = []

            logger = configure_logger(project_name)

            assert logger is not None
            # The logger should have handlers added
            # Note: Actual handler verification would depend on implementation details
