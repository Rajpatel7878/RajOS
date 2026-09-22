from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str
    content: str
    title: Optional[str] = None
    mime_type: Optional[str] = "text/plain"


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    title: Optional[str] = None
    content: str
    mime_type: str
    file_size: int
    status: str
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


class SearchHit(BaseModel):
    chunk_id: str
    document_id: int
    filename: str
    heading: str
    content: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchHit]


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    ready_documents: int
    processing_documents: int
    failed_documents: int
    total_chunks: int
    total_file_size_bytes: int
