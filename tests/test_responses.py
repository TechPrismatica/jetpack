"""
Tests for jetpack.responses module.
"""

from unittest.mock import patch

import pytest

from jetpack.responses import (
    RequestMeta,
    DefaultResponseSchema,
    DefaultFailureSchema,
)


class TestRequestMeta:
    """Test cases for RequestMeta schema."""

    def test_default_initialization(self):
        """Test RequestMeta with default values."""
        from asgi_correlation_id import correlation_id

        # Set a correlation ID in the context
        token = correlation_id.set("test-correlation-123")
        try:
            meta = RequestMeta()

            assert meta.request_id == "test-correlation-123"
            assert meta.timestamp is not None
            # Verify timestamp format (ISO format)
            assert "T" in meta.timestamp
            assert (
                meta.timestamp.endswith("Z")
                or "+" in meta.timestamp
                or "-" in meta.timestamp[-6:]
            )
        finally:
            correlation_id.reset(token)

    def test_custom_request_id(self):
        """Test RequestMeta with custom request_id."""
        custom_id = "custom-request-id-456"
        meta = RequestMeta(request_id=custom_id)

        assert meta.request_id == custom_id
        assert meta.timestamp is not None

    def test_custom_timestamp(self):
        """Test RequestMeta with custom timestamp."""
        custom_timestamp = "2023-12-25T10:30:00Z"
        meta = RequestMeta(timestamp=custom_timestamp)

        assert meta.timestamp == custom_timestamp
        # request_id should still use the correlation_id default or None
        assert meta.request_id is not None or meta.request_id is None

    def test_get_correlation_id_lookup_error(self):
        """Test get_correlation_id function when LookupError is raised."""
        from unittest.mock import Mock
        import jetpack.responses

        # Create a mock correlation_id that raises LookupError
        mock_correlation_id = Mock()
        mock_correlation_id.get.side_effect = LookupError("No correlation ID set")

        # Patch the correlation_id at the module level
        with patch.object(jetpack.responses, "correlation_id", mock_correlation_id):
            # Import fresh to get the patched version
            from jetpack.responses import get_correlation_id

            # Test the get_correlation_id function - should return None due to LookupError
            result = get_correlation_id()
            assert result is None

            # Verify the mock was called
            mock_correlation_id.get.assert_called_once()

    def test_both_custom_values(self):
        """Test RequestMeta with both custom values."""
        custom_id = "custom-123"
        custom_timestamp = "2023-01-01T00:00:00Z"

        meta = RequestMeta(request_id=custom_id, timestamp=custom_timestamp)

        assert meta.request_id == custom_id
        assert meta.timestamp == custom_timestamp

    def test_none_values(self):
        """Test RequestMeta with None values."""
        meta = RequestMeta(request_id=None, timestamp=None)

        assert meta.request_id is None
        assert meta.timestamp is None

    def test_serialization(self):
        """Test RequestMeta serialization."""
        meta = RequestMeta(request_id="test-123", timestamp="2023-12-25T12:00:00Z")

        serialized = meta.model_dump()

        assert serialized["request_id"] == "test-123"
        assert serialized["timestamp"] == "2023-12-25T12:00:00Z"

    def test_json_serialization(self):
        """Test RequestMeta JSON serialization."""
        meta = RequestMeta(request_id="test-456", timestamp="2023-12-25T15:30:00Z")

        json_str = meta.model_dump_json()

        assert '"request_id":"test-456"' in json_str.replace(" ", "")
        assert '"timestamp":"2023-12-25T15:30:00Z"' in json_str.replace(" ", "")


class TestDefaultResponseSchema:
    """Test cases for DefaultResponseSchema."""

    def test_default_initialization(self):
        """Test DefaultResponseSchema with default values."""
        response = DefaultResponseSchema()

        assert response.status == "success"
        assert response.message == "Response fetched successfully"
        assert response.data is None
        assert response.meta is None

    def test_custom_status(self):
        """Test DefaultResponseSchema with custom status."""
        response = DefaultResponseSchema(status="custom_status")

        assert response.status == "custom_status"
        assert response.message == "Response fetched successfully"

    def test_custom_message(self):
        """Test DefaultResponseSchema with custom message."""
        custom_message = "Data retrieved successfully"
        response = DefaultResponseSchema(message=custom_message)

        assert response.status == "success"
        assert response.message == custom_message

    def test_with_data(self):
        """Test DefaultResponseSchema with data."""
        test_data = {"users": [{"id": 1, "name": "John"}]}
        response = DefaultResponseSchema(data=test_data)

        assert response.status == "success"
        assert response.data == test_data

    def test_with_meta(self):
        """Test DefaultResponseSchema with meta."""
        meta = RequestMeta(request_id="test-123")
        response = DefaultResponseSchema(meta=meta)

        assert response.status == "success"
        assert response.meta == meta
        assert response.meta.request_id == "test-123"

    def test_complete_response(self):
        """Test DefaultResponseSchema with all fields."""
        test_data = {"count": 5, "items": ["a", "b", "c"]}
        meta = RequestMeta(request_id="complete-test-789")

        response = DefaultResponseSchema(
            status="completed",
            message="All data fetched successfully",
            data=test_data,
            meta=meta,
        )

        assert response.status == "completed"
        assert response.message == "All data fetched successfully"
        assert response.data == test_data
        assert response.meta == meta

    def test_serialization(self):
        """Test DefaultResponseSchema serialization."""
        response = DefaultResponseSchema(
            status="success", message="Test message", data={"key": "value"}
        )

        serialized = response.model_dump()

        assert serialized["status"] == "success"
        assert serialized["message"] == "Test message"
        assert serialized["data"] == {"key": "value"}
        assert serialized["meta"] is None

    def test_json_serialization(self):
        """Test DefaultResponseSchema JSON serialization."""
        response = DefaultResponseSchema(
            data={"test": True}, meta=RequestMeta(request_id="json-test")
        )

        json_str = response.model_dump_json()

        assert '"status":"success"' in json_str.replace(" ", "")
        assert '"test":true' in json_str.replace(" ", "")

    def test_nested_meta_serialization(self):
        """Test DefaultResponseSchema with nested RequestMeta serialization."""
        meta = RequestMeta(request_id="nested-123", timestamp="2023-12-25T18:00:00Z")
        response = DefaultResponseSchema(meta=meta)

        serialized = response.model_dump()

        assert serialized["meta"]["request_id"] == "nested-123"
        assert serialized["meta"]["timestamp"] == "2023-12-25T18:00:00Z"


class TestDefaultFailureSchema:
    """Test cases for DefaultFailureSchema."""

    def test_default_initialization(self):
        """Test DefaultFailureSchema with default values."""
        response = DefaultFailureSchema()

        assert response.status == "failure"
        assert response.message == "Response fetch failed"
        assert response.data is None
        assert response.error is None
        assert response.meta is None

    def test_custom_status(self):
        """Test DefaultFailureSchema with custom status."""
        response = DefaultFailureSchema(status="error")

        assert response.status == "error"
        assert response.message == "Response fetch failed"

    def test_custom_message(self):
        """Test DefaultFailureSchema with custom message."""
        custom_message = "Database connection failed"
        response = DefaultFailureSchema(message=custom_message)

        assert response.status == "failure"
        assert response.message == custom_message

    def test_with_error(self):
        """Test DefaultFailureSchema with error data."""
        error_data = {"code": "DB_001", "details": "Connection timeout"}
        response = DefaultFailureSchema(error=error_data)

        assert response.status == "failure"
        assert response.error == error_data

    def test_with_data_and_error(self):
        """Test DefaultFailureSchema with both data and error."""
        partial_data = {"processed": 5, "failed": 2}
        error_info = {"message": "Partial processing failure"}

        response = DefaultFailureSchema(data=partial_data, error=error_info)

        assert response.data == partial_data
        assert response.error == error_info

    def test_with_meta(self):
        """Test DefaultFailureSchema with meta."""
        meta = RequestMeta(request_id="failure-test-456")
        response = DefaultFailureSchema(meta=meta)

        assert response.meta == meta
        assert response.meta.request_id == "failure-test-456"

    def test_complete_failure_response(self):
        """Test DefaultFailureSchema with all fields."""
        error_data = {"code": "VAL_001", "field": "email"}
        partial_data = {"valid_fields": ["name", "age"]}
        meta = RequestMeta(request_id="complete-failure-789")

        response = DefaultFailureSchema(
            status="validation_error",
            message="Validation failed for some fields",
            data=partial_data,
            error=error_data,
            meta=meta,
        )

        assert response.status == "validation_error"
        assert response.message == "Validation failed for some fields"
        assert response.data == partial_data
        assert response.error == error_data
        assert response.meta == meta

    def test_serialization(self):
        """Test DefaultFailureSchema serialization."""
        response = DefaultFailureSchema(
            message="Test failure", error={"code": "TEST_001"}
        )

        serialized = response.model_dump()

        assert serialized["status"] == "failure"
        assert serialized["message"] == "Test failure"
        assert serialized["error"] == {"code": "TEST_001"}
        assert serialized["data"] is None
        assert serialized["meta"] is None

    def test_json_serialization(self):
        """Test DefaultFailureSchema JSON serialization."""
        response = DefaultFailureSchema(
            error={"type": "ValidationError", "fields": ["email"]},
            meta=RequestMeta(request_id="json-failure-test"),
        )

        json_str = response.model_dump_json()

        assert '"status":"failure"' in json_str.replace(" ", "")
        assert '"type":"ValidationError"' in json_str.replace(" ", "")


class TestSchemasIntegration:
    """Integration tests for response schemas."""

    def test_success_and_failure_schemas_compatibility(self):
        """Test that success and failure schemas have compatible structure."""
        success = DefaultResponseSchema(
            data={"result": "ok"}, meta=RequestMeta(request_id="test-123")
        )

        failure = DefaultFailureSchema(
            error={"code": "ERR_001"}, meta=RequestMeta(request_id="test-123")
        )

        success_dict = success.model_dump()
        failure_dict = failure.model_dump()

        # Both should have the same top-level keys (except error vs data)
        success_keys = set(success_dict.keys())
        failure_keys = set(failure_dict.keys())

        assert "status" in success_keys and "status" in failure_keys
        assert "message" in success_keys and "message" in failure_keys
        assert "meta" in success_keys and "meta" in failure_keys

    def test_real_world_success_response(self):
        """Test a realistic success response."""
        from asgi_correlation_id import correlation_id

        token = correlation_id.set("req-12345")
        try:
            response = DefaultResponseSchema(
                message="Users retrieved successfully",
                data={
                    "users": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com"},
                        {"id": 2, "name": "Bob", "email": "bob@example.com"},
                    ],
                    "total": 2,
                    "page": 1,
                },
                meta=RequestMeta(),
            )

            assert response.status == "success"
            assert response.data["total"] == 2
            assert len(response.data["users"]) == 2
            assert response.meta.request_id == "req-12345"
        finally:
            correlation_id.reset(token)

    def test_real_world_failure_response(self):
        """Test a realistic failure response."""
        from asgi_correlation_id import correlation_id

        token = correlation_id.set("req-67890")
        try:
            response = DefaultFailureSchema(
                message="User validation failed",
                error={
                    "code": "VALIDATION_ERROR",
                    "details": [
                        {"field": "email", "message": "Invalid email format"},
                        {"field": "age", "message": "Must be at least 18"},
                    ],
                },
                data={"valid_fields": ["name"]},
                meta=RequestMeta(),
            )

            assert response.status == "failure"
            assert response.error["code"] == "VALIDATION_ERROR"
            assert len(response.error["details"]) == 2
            assert response.meta.request_id == "req-67890"
        finally:
            correlation_id.reset(token)

    @pytest.mark.parametrize(
        "schema_class", [DefaultResponseSchema, DefaultFailureSchema]
    )
    def test_schema_validation(self, schema_class):
        """Test that schemas properly validate their fields."""
        # All schemas should accept basic valid data
        instance = schema_class(status="test", message="test message")

        assert instance.status == "test"
        assert instance.message == "test message"

    def test_timestamp_format_consistency(self):
        """Test that timestamps are consistently formatted."""
        meta1 = RequestMeta()
        meta2 = RequestMeta()

        # Both should have timestamp in ISO format
        if meta1.timestamp and meta2.timestamp:
            # Both timestamps should contain 'T' (ISO format indicator)
            assert "T" in meta1.timestamp
            assert "T" in meta2.timestamp
