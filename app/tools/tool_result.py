from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolErrorCode(str, Enum):
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_DISABLED = "TOOL_DISABLED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_ARGUMENTS = "INVALID_ARGUMENTS"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    TIMEOUT = "TIMEOUT"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"


class ToolError(BaseModel):
    code: ToolErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None


class ToolResult(BaseModel):
    success: bool
    tool_name: str
    data: Optional[Any] = None
    error: Optional[ToolError] = None
    execution_time_ms: float = 0.0
    requires_confirmation: bool = False
    confirmation_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.dict(exclude_none=True)
