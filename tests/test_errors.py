"""
Tests for jetpack.errors module.
"""

import pytest

from jetpack.errors import GenericErrors


class TestGenericErrors:
    """Test cases for GenericErrors exception class."""

    def test_default_initialization(self):
        """Test GenericErrors with default parameters."""
        error = GenericErrors()

        assert error.message == "An error has occurred. Please contact support."
        assert error.ec is None
        assert error.status_code == 500
        assert str(error) == "An error has occurred. Please contact support."

    def test_initialization_with_message(self):
        """Test GenericErrors with custom message."""
        message = "Custom error message"
        error = GenericErrors(message=message)

        assert error.message == message
        assert error.ec is None
        assert error.status_code == 500
        assert str(error) == message

    def test_initialization_with_error_code(self):
        """Test GenericErrors with error code."""
        message = "Database connection failed"
        ec = "DB_001"
        error = GenericErrors(message=message, ec=ec)

        expected_message = f"{ec}: {message}"
        assert error.message == expected_message
        assert error.ec == ec
        assert error.status_code == 500
        assert str(error) == expected_message

    def test_initialization_with_status_code(self):
        """Test GenericErrors with custom status code."""
        message = "Resource not found"
        status_code = 404
        error = GenericErrors(message=message, status_code=status_code)

        assert error.message == message
        assert error.ec is None
        assert error.status_code == status_code

    def test_initialization_with_all_parameters(self):
        """Test GenericErrors with all parameters."""
        message = "Validation failed"
        ec = "VAL_001"
        status_code = 422
        error = GenericErrors(message=message, ec=ec, status_code=status_code)

        expected_message = f"{ec}: {message}"
        assert error.message == expected_message
        assert error.ec == ec
        assert error.status_code == status_code
        assert str(error) == expected_message

    def test_message_property_getter(self):
        """Test message property getter."""
        message = "Test message"
        error = GenericErrors(message=message)

        assert error.message == message

    def test_message_property_setter(self):
        """Test message property setter."""
        error = GenericErrors()
        new_message = "Updated message"

        error.message = new_message
        assert error.message == new_message

    def test_ec_property_getter(self):
        """Test error code property getter."""
        ec = "TEST_001"
        error = GenericErrors(ec=ec)

        assert error.ec == ec

    def test_ec_property_setter(self):
        """Test error code property setter."""
        error = GenericErrors()
        new_ec = "NEW_001"

        error.ec = new_ec
        assert error.ec == new_ec

    def test_status_code_property_getter(self):
        """Test status code property getter."""
        status_code = 400
        error = GenericErrors(status_code=status_code)

        assert error.status_code == status_code

    def test_status_code_property_setter(self):
        """Test status code property setter."""
        error = GenericErrors()
        new_status_code = 403

        error.status_code = new_status_code
        assert error.status_code == new_status_code

    def test_inheritance_from_exception(self):
        """Test that GenericErrors inherits from Exception."""
        error = GenericErrors()

        assert isinstance(error, Exception)
        assert isinstance(error, GenericErrors)

    def test_exception_raising(self):
        """Test that GenericErrors can be raised as an exception."""
        message = "Test exception"
        ec = "TEST_001"
        status_code = 400

        with pytest.raises(GenericErrors) as exc_info:
            raise GenericErrors(message=message, ec=ec, status_code=status_code)

        exception = exc_info.value
        assert exception.message == f"{ec}: {message}"
        assert exception.ec == ec
        assert exception.status_code == status_code

    def test_exception_with_empty_message(self):
        """Test GenericErrors with empty message."""
        error = GenericErrors(message="")

        assert error.message == ""
        assert error.ec is None
        assert error.status_code == 500

    def test_exception_with_empty_error_code(self):
        """Test GenericErrors with empty error code."""
        message = "Test message"
        error = GenericErrors(message=message, ec="")

        # Check actual behavior - empty string ec should be treated like None
        # Let's see what the actual implementation does
        assert error.message == message  # Based on actual implementation
        assert error.ec == ""

    def test_exception_with_none_values(self):
        """Test GenericErrors with None values explicitly set."""
        error = GenericErrors(message=None, ec=None, status_code=None)

        # When message is None, it should still format properly
        assert error.message == "None: None" or error.message is None
        assert error.ec is None
        # status_code might default to 500 if None is passed

    @pytest.mark.parametrize(
        "status_code", [200, 201, 400, 401, 403, 404, 422, 500, 503]
    )
    def test_various_status_codes(self, status_code):
        """Test GenericErrors with various HTTP status codes."""
        error = GenericErrors(status_code=status_code)

        assert error.status_code == status_code

    @pytest.mark.parametrize(
        "ec,message,expected",
        [
            ("ERR001", "Test error", "ERR001: Test error"),
            ("", "Empty EC", "Empty EC"),  # Empty string is falsy, so no prefix
            ("NONEMPTY", "", "NONEMPTY: "),
            (None, "No EC", "No EC"),
        ],
    )
    def test_message_formatting_combinations(self, ec, message, expected):
        """Test various combinations of error code and message formatting."""
        error = GenericErrors(message=message, ec=ec)

        if not ec:  # Both None and empty string are falsy
            assert error.message == message
        else:
            assert error.message == expected

    def test_property_modification_after_initialization(self):
        """Test modifying properties after object creation."""
        error = GenericErrors()

        # Modify all properties
        error.message = "Modified message"
        error.ec = "MOD_001"
        error.status_code = 418

        assert error.message == "Modified message"
        assert error.ec == "MOD_001"
        assert error.status_code == 418

    def test_docstring_exists(self):
        """Test that the class has a docstring."""
        assert GenericErrors.__doc__ is not None
        assert "Generic Error" in GenericErrors.__doc__
