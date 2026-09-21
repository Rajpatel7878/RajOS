from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class MemoryBase(BaseModel):
    key: str
    value: str
    content: Optional[str] = None
    memory_type: str = Field(default="preference", description="preference | goal | project | instruction | fact")
    confidence: str = Field(default="high", description="low | medium | high")
    importance: str = Field(default="medium", description="low | medium | high | critical")


class MemoryCreate(MemoryBase):
    source: str = Field(default="explicit_user", description="explicit_user | inferred_llm | system")


class MemoryUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    content: Optional[str] = None
    memory_type: Optional[str] = None
    confidence: Optional[str] = None
    importance: Optional[str] = None
    status: Optional[str] = None


class MemoryResponse(MemoryBase):
    id: int
    user_id: int
    source: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0

    class Config:
        from_attributes = True


class ExplicitMemoryRequest(BaseModel):
    user_message: str


class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    memory_type: Optional[str] = None


class MemoryStatsResponse(BaseModel):
    total_memories: int
    active_memories: int
    by_type: dict[str, int] = {}
    by_source: dict[str, int] = {}
