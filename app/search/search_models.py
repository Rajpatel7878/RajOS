"""API and service schemas for RajOS unified search."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

ResourceType = Literal[
    "tasks",
    "notes",
    "documents",
    "conversations",
    "memories",
    "knowledge",
]

SortOption = Literal["relevance", "newest", "oldest"]

RESOURCE_TYPE_VALUES: tuple[str, ...] = (
    "tasks",
    "notes",
    "documents",
    "conversations",
    "memories",
    "knowledge",
)

_MAX_QUERY_LENGTH = 200


class SearchFilters(BaseModel):
    """Validated filters shared by the API, service and tool layers."""

    resource_types: List[str] = Field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort: SortOption = "relevance"
    semantic: bool = False

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _validate_range(self) -> "SearchFilters":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be earlier than or equal to date_to")
        return self


class AppliedSearchFilters(BaseModel):
    """Filters actually applied to a response."""

    resource_types: List[str]
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort: SortOption = "relevance"
    semantic: bool = False


class SearchItem(BaseModel):
    """One unified search result, independent of resource type."""

    id: str
    resource_id: str
    resource_type: str
    title: str
    snippet: str
    url: Optional[str] = None
    matched_fields: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderStatus(BaseModel):
    """Per-provider outcome so partial failures are visible and honest."""

    resource_type: str
    display_name: str
    status: Literal["ok", "error", "disabled", "skipped"]
    result_count: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None


class SearchPagination(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class UnifiedSearchResponse(BaseModel):
    query: str
    items: List[SearchItem] = Field(default_factory=list)
    pagination: SearchPagination
    filters: AppliedSearchFilters
    providers: List[ProviderStatus] = Field(default_factory=list)
    took_ms: float = 0.0


class SearchSuggestion(BaseModel):
    text: str
    kind: Literal["history", "resource"]
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    url: Optional[str] = None


class SuggestionResponse(BaseModel):
    query: str
    suggestions: List[SearchSuggestion] = Field(default_factory=list)


class SearchHistoryItem(BaseModel):
    id: int
    query: str
    resource_types: List[str] = Field(default_factory=list)
    result_count: int = 0
    searched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchHistoryResponse(BaseModel):
    items: List[SearchHistoryItem] = Field(default_factory=list)


class ClearHistoryResponse(BaseModel):
    cleared: int


class ResourceTypeInfo(BaseModel):
    value: str
    label: str
    available: bool
    reason: Optional[str] = None


class SortInfo(BaseModel):
    value: SortOption
    label: str


class SearchFilterOptions(BaseModel):
    resource_types: List[ResourceTypeInfo]
    sorts: List[SortInfo]
    semantic_available: bool
    max_limit: int
    max_query_length: int
