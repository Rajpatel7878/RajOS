"""Authenticated unified search API.

Route prefix: ``/search`` (unchanged from the legacy search endpoint).
All workspace searches require a valid bearer token and are scoped to the
authenticated user derived from it.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.search.history_service import search_history_service
from app.search.search_models import (
    ClearHistoryResponse,
    SearchFilterOptions,
    SearchHistoryResponse,
    SuggestionResponse,
    UnifiedSearchResponse,
)
from app.search.unified_search_service import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MAX_PAGE,
    unified_search_service,
)
from app.search.utils.scoring import MAX_QUERY_LENGTH
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

SortQuery = Literal["relevance", "newest", "oldest"]


def _requested_types(types: Optional[str], legacy_type: str) -> List[str]:
    """Combine the multi-type ``types`` parameter with the legacy ``type`` one."""
    requested: List[str] = []
    if legacy_type and legacy_type.strip().lower() != "all":
        requested.append(legacy_type.strip())
    if types:
        requested.extend(part.strip() for part in types.split(",") if part.strip())
    return requested


@router.get("", response_model=UnifiedSearchResponse)
@router.get("/", response_model=UnifiedSearchResponse, include_in_schema=False)
def unified_search(
    q: str = Query("", max_length=MAX_QUERY_LENGTH, description="Search query"),
    type: str = Query("all", description="Legacy single resource type filter"),
    types: Optional[str] = Query(
        None,
        description="Comma-separated resource types: tasks,notes,documents,conversations,memories,knowledge",
    ),
    sort: SortQuery = Query("relevance", description="relevance, newest or oldest"),
    date_from: Optional[datetime] = Query(None, description="Only results updated at/after this time"),
    date_to: Optional[datetime] = Query(None, description="Only results updated at/before this time"),
    page: int = Query(1, ge=1, le=MAX_PAGE),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    semantic: bool = Query(False, description="Include semantic knowledge-base retrieval"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Search the authenticated user's workspace across supported resources."""
    requested = _requested_types(types, type)

    try:
        return unified_search_service.search(
            db=db,
            user_id=user.id,
            query=q,
            resource_types=requested,
            sort=sort,
            date_from=date_from,
            date_to=date_to,
            page=page,
            limit=limit,
            semantic=semantic,
        )
    except ValueError as exc:
        # Safe validation message (e.g. unsupported resource type / date range).
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/suggestions", response_model=SuggestionResponse)
def search_suggestions(
    q: str = Query("", max_length=MAX_QUERY_LENGTH),
    limit: int = Query(8, ge=1, le=10),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Recent searches plus bounded title suggestions for this user only."""
    suggestions = unified_search_service.suggestions(
        db=db,
        user_id=user.id,
        query=q,
        limit=limit,
    )
    return SuggestionResponse(query=q, suggestions=suggestions)


@router.get("/history", response_model=SearchHistoryResponse)
def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return the authenticated user's most recent searches."""
    return SearchHistoryResponse(items=search_history_service.list(db, user.id, limit=limit))


@router.delete("/history", response_model=ClearHistoryResponse)
def clear_search_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Clear only the authenticated user's search history."""
    return ClearHistoryResponse(cleared=search_history_service.clear(db, user.id))


@router.get("/filters", response_model=SearchFilterOptions)
def search_filter_options(
    _: User = Depends(get_current_user),
):
    """Supported resource types, sort options and limits."""
    return unified_search_service.get_filter_options()
