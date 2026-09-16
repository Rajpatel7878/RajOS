from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    agent_id: Optional[str] = None  # 'atlas', 'nova', 'sage', 'echo', 'pulse'
    attachments: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str

    class Config:
        from_attributes = True
