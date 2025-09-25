from typing import Any, Optional
from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field
from whenever import Instant


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID value."""
    try:
        return correlation_id.get()
    except LookupError:
        return None


def get_current_timestamp() -> str:
    """Get the current timestamp in ISO format."""
    return Instant.now().format_common_iso()


class RequestMeta(BaseModel):
    request_id: Optional[str] = Field(default_factory=get_correlation_id)
    timestamp: Optional[str] = Field(default_factory=get_current_timestamp)


class DefaultResponseSchema(BaseModel):
    status: str = "success"
    message: str = "Response fetched successfully"
    data: Optional[Any] = None
    meta: Optional[RequestMeta] = None


class DefaultFailureSchema(BaseModel):
    status: str = "failure"
    message: str = "Response fetch failed"
    data: Optional[Any] = None
    error: Optional[Any] = None
    meta: Optional[RequestMeta] = None
