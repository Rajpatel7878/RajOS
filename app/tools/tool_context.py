from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolExecutionContext(BaseModel):
    user_id: int
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_permission(self, required_permission: str) -> bool:
        if "*" in self.permissions or "admin" in self.permissions:
            return True
        return required_permission in self.permissions
