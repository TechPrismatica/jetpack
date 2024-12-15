from typing import Any, Optional

from pydantic import BaseModel
from whenever import Instant


class ResponseMeta(BaseModel):
    request_id: Optional[str] = None
    timestamp: Optional[str] = Instant.now().format_common_iso()


class DefaultResponseSchema(BaseModel):
    status: str = "success"
    message: str = "Response fetched successfully"
    data: Optional[Any] = None
    meta: Optional[ResponseMeta] = None


class DefaultFailureSchema(BaseModel):
    status: str = "failure"
    message: str = "Response fetch failed"
    data: Optional[Any] = None
    error: Optional[Any] = None
