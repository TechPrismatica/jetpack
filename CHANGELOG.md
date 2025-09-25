# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-09-25

### Added
- Comprehensive test suite with 100% coverage (127 tests)
- Complete documentation in README.md
- GitHub Copilot instructions for development guidance
- Type hints throughout the codebase
- Pydantic-based configuration management
- Structured logging with correlation ID support
- FastAPI exception handlers
- Standardized response schemas

### Fixed
- Configuration path handling for None values
- ContextVar correlation ID integration
- Request validation error handling compatibility

### Changed
- Improved `RequestMeta` to use factory functions for defaults
- Enhanced error message formatting in `GenericErrors`
- Updated logging configuration with better validation

## [0.1.0] - Initial Release

### Added
- Basic configuration management (`config.py`)
- Error handling framework (`errors/`)
- Logging configuration (`log_config.py`)
- Response schemas (`responses.py`)
- Core utility functions for microservice development

### Features
- Environment-based configuration
- Custom exception classes
- Correlation ID tracking
- Structured logging setup
- Pydantic response models
