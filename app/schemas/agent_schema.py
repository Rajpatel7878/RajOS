from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    system_instructions: str = Field(..., min_length=1)
    capabilities: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    memory_policy: str = Field("read_write", description="none, read, read_write")
    knowledge_access: str = Field("search", description="none, search, full")
    max_steps: int = Field(5, ge=1, le=20)
    max_tool_calls: int = Field(5, ge=1, le=20)
    timeout_seconds: float = Field(30.0, ge=5.0, le=120.0)
    confirmation_policy: str = Field("default", description="default, always, never")
    enabled: bool = True


class AgentCreate(AgentBase):
    id: Optional[str] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_instructions: Optional[str] = None
    capabilities: Optional[List[str]] = None
    allowed_tools: Optional[List[str]] = None
    memory_policy: Optional[str] = None
    knowledge_access: Optional[str] = None
    max_steps: Optional[int] = None
    max_tool_calls: Optional[int] = None
    timeout_seconds: Optional[float] = None
    confirmation_policy: Optional[str] = None
    enabled: Optional[bool] = None


class AgentResponse(AgentBase):
    id: str
    is_builtin: bool = False
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AgentRunRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    confirmation: Optional[Dict[str, Any]] = None


class AgentRunResponse(BaseModel):
    run_id: str
    agent_id: str
    agent_name: str
    status: str
    response: Optional[str] = None
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    requires_confirmation: Optional[bool] = False
    confirmation_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentRunDetail(BaseModel):
    id: str
    user_id: int
    agent_id: str
    conversation_id: Optional[int] = None
    prompt: str
    status: str
    current_step: int
    step_history: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: Optional[str] = None
    error_message: Optional[str] = None
    confirmation_token: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
