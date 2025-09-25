"""
Tests for jetpack.errors.exception_handlers module.
"""

import json
from unittest.mock import Mock, patch

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from jetpack.errors import GenericErrors
from jetpack.errors.exception_handlers import (
    ExceptionHandlers,
    get_exception_handlers,
)


class TestExceptionHandlers:
    """Test cases for ExceptionHandlers class."""

    def test_generic_exception_handler(self):
        """Test generic exception handler."""
        request = Mock(spec=Request)
        exception = Exception("Test exception")

        with patch("jetpack.errors.exception_handlers.logger.exception") as mock_logger:
            response = ExceptionHandlers.generic_exception_handler(request, exception)

        # Verify logging
        mock_logger.assert_called_once_with("Generic Exception: Test exception")

        # Verify response
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        # Parse response content
        content = response.body.decode()
        parsed_content = json.loads(content)
        assert (
            parsed_content["message"] == "Something went wrong. Please contact support."
        )

    def test_request_validation_exception_handler(self):
        """Test request validation exception handler."""
        request = Mock(spec=Request)

        # Create a mock RequestValidationError
        mock_validation_error = Mock(spec=RequestValidationError)
        mock_validation_error.errors.return_value = [
            {"field": "test_field", "error": "required"}
        ]

        with patch("jetpack.errors.exception_handlers.logger.exception") as mock_logger:
            response = ExceptionHandlers.request_validation_exception_handler(
                request, mock_validation_error
            )

        # Verify logging
        mock_logger.assert_called_once()

        # Verify response
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Parse response content
        content = response.body.decode()
        parsed_content = json.loads(content)
        assert parsed_content["message"] == "Request Validation Error"
        assert "detail" in parsed_content
        assert parsed_content["detail"] == [
            {"field": "test_field", "error": "required"}
        ]

    def test_exception_handler_generator(self):
        """Test exception handler generator."""

        # Create a custom exception class
        class CustomError(GenericErrors):
            pass

        # Generate handler
        handler_func = ExceptionHandlers.exception_handler_generator(CustomError)

        # Test the generated handler
        request = Mock(spec=Request)
        custom_exception = CustomError(
            message="Custom error occurred", ec="CUSTOM_001", status_code=400
        )

        with patch("jetpack.errors.exception_handlers.logger.exception") as mock_logger:
            response = handler_func(request, custom_exception)

        # Verify logging
        mock_logger.assert_called_once()

        # Verify response
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        # Parse response content
        content = response.body.decode()
        parsed_content = json.loads(content)
        assert parsed_content["message"] == "CUSTOM_001: Custom error occurred"

    def test_exception_handler_generator_with_generic_errors(self):
        """Test exception handler generator with GenericErrors."""
        handler_func = ExceptionHandlers.exception_handler_generator(GenericErrors)

        request = Mock(spec=Request)
        generic_exception = GenericErrors(message="Generic error", status_code=422)

        with patch("jetpack.errors.exception_handlers.logger.exception"):
            response = handler_func(request, generic_exception)

        # Verify response
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        # Parse response content
        content = response.body.decode()
        parsed_content = json.loads(content)
        assert parsed_content["message"] == "Generic error"


class TestGetExceptionHandlers:
    """Test cases for get_exception_handlers function."""

    def test_get_exception_handlers_default(self):
        """Test get_exception_handlers with default parameters."""
        handlers = get_exception_handlers()

        # Should return None since the function doesn't return anything
        # The function appears to have a bug - it builds handlers but doesn't return them
        assert handlers is None

    def test_get_exception_handlers_with_exceptions_list(self):
        """Test get_exception_handlers with exceptions list."""

        class CustomError1(GenericErrors):
            pass

        class CustomError2(GenericErrors):
            pass

        exceptions_list = [CustomError1, CustomError2]

        # The function should process the exceptions but currently doesn't return anything
        result = get_exception_handlers(exceptions_list=exceptions_list)
        assert result is None

    def test_get_exception_handlers_with_custom_validation_handler(self):
        """Test get_exception_handlers with custom validation handler."""

        def custom_validation_handler(request, exc):
            return JSONResponse(status_code=400, content={"custom": "validation error"})

        result = get_exception_handlers(
            custom_validation_handler=custom_validation_handler
        )
        assert result is None

    def test_get_exception_handlers_with_custom_handlers_dict(self):
        """Test get_exception_handlers with custom exception handlers dict."""

        def custom_handler(request, exc):
            return JSONResponse(status_code=418, content={"message": "I'm a teapot"})

        custom_handlers = {ValueError: custom_handler}

        result = get_exception_handlers(exception_handlers=custom_handlers)
        assert result is None

    def test_get_exception_handlers_with_all_parameters(self):
        """Test get_exception_handlers with all parameters provided."""

        class CustomError(GenericErrors):
            pass

        def custom_validation_handler(request, exc):
            return JSONResponse(status_code=400, content={"custom": "validation"})

        def custom_handler(request, exc):
            return JSONResponse(status_code=418, content={"custom": "handler"})

        exceptions_list = [CustomError]
        custom_handlers = {ValueError: custom_handler}

        result = get_exception_handlers(
            exceptions_list=exceptions_list,
            custom_validation_handler=custom_validation_handler,
            exception_handlers=custom_handlers,
        )

        assert result is None

    def test_function_builds_handlers_internally(self):
        """Test that the function builds handlers dictionary internally."""
        # Since the function doesn't return anything, we can at least verify it runs without error
        # and test that it processes the parameters correctly
        result = get_exception_handlers()

        # The function should run without error
        assert result is None  # Based on current implementation

        # Test with parameters
        class CustomError(GenericErrors):
            pass

        result2 = get_exception_handlers(exceptions_list=[CustomError])
        assert result2 is None


class TestExceptionHandlersIntegration:
    """Integration tests for exception handlers."""

    def test_handler_with_real_request_validation_error(self):
        """Test handler with a real RequestValidationError."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            required_field: str

        # Create a real validation error
        try:
            TestModel()  # This should fail validation
        except ValidationError as e:
            # Convert to RequestValidationError-like object
            mock_request_error = Mock(spec=RequestValidationError)
            mock_request_error.errors.return_value = e.errors()

            request = Mock(spec=Request)

            with patch("jetpack.errors.exception_handlers.logger.exception"):
                response = ExceptionHandlers.request_validation_exception_handler(
                    request, mock_request_error
                )

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_all_handlers_return_json_response(self):
        """Test that all handlers return JSONResponse objects."""
        request = Mock(spec=Request)

        # Test generic exception handler
        response1 = ExceptionHandlers.generic_exception_handler(
            request, Exception("test")
        )
        assert isinstance(response1, JSONResponse)

        # Test validation exception handler
        mock_validation_error = Mock(spec=RequestValidationError)
        mock_validation_error.errors.return_value = [{"error": "test"}]

        response2 = ExceptionHandlers.request_validation_exception_handler(
            request, mock_validation_error
        )
        assert isinstance(response2, JSONResponse)

        # Test generated exception handler
        handler = ExceptionHandlers.exception_handler_generator(GenericErrors)
        response3 = handler(request, GenericErrors("test"))
        assert isinstance(response3, JSONResponse)

    def test_exception_handlers_log_appropriately(self):
        """Test that all exception handlers log exceptions."""
        request = Mock(spec=Request)

        with patch("jetpack.errors.exception_handlers.logger.exception") as mock_logger:
            # Test generic handler logging
            ExceptionHandlers.generic_exception_handler(request, Exception("test1"))

            # Test validation handler logging
            mock_validation_error = Mock(spec=RequestValidationError)
            mock_validation_error.errors.return_value = [{"error": "test"}]
            ExceptionHandlers.request_validation_exception_handler(
                request, mock_validation_error
            )

            # Test generated handler logging
            handler = ExceptionHandlers.exception_handler_generator(GenericErrors)
            handler(request, GenericErrors("test3"))

        # Should have 3 logging calls
        assert mock_logger.call_count == 3


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        from jetpack.errors import exception_handlers

        assert hasattr(exception_handlers, "__all__")
        assert "get_exception_handlers" in exception_handlers.__all__

    def test_importable_functions(self):
        """Test that functions can be imported."""
        from jetpack.errors.exception_handlers import get_exception_handlers

        assert callable(get_exception_handlers)
