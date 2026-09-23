from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    agent_id: Optional[str] = None  # 'atlas', 'nova', 'sage', 'echo', 'pulse'
    attachments: Optional[List[Dict[str, Any]]] = None
    confirmation: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    memory: Optional[List[Any]] = None
    conversation_context: Optional[Any] = None
    agent: Optional[Any] = None
    sources: Optional[List[Dict[str, Any]]] = None
    requires_confirmation: Optional[bool] = None
    confirmation_details: Optional[Dict[str, Any]] = None
    tool_executions: Optional[List[Dict[str, Any]]] = None


class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# MessageResponse alias for backward-compatibility
MessageResponse = MessageRead


class ConversationRead(BaseModel):
    id: int
    title: Optional[str] = None
    user_title: bool = False
    archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationDetail(ConversationRead):
    messages: List[MessageRead] = []


class ConversationRename(BaseModel):
    title: str


class ConversationArchive(BaseModel):
    archived: bool = True
