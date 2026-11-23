"""Unified search across the RajOS workspace.

Pipeline::

    authenticated user
        -> query normalization
        -> per-provider, user-scoped retrieval
        -> deduplication + deterministic ranking
        -> filters / sorting / pagination
        -> consistent result schema + provider status

Providers never receive a client-supplied user id, never build raw SQL and are
isolated from each other: one failure is reported in ``providers`` while the
remaining results are still returned.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.search.history_service import SearchHistoryService, search_history_service
from app.search.providers import default_providers
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider
from app.search.search_models import (
    AppliedSearchFilters,
    ProviderStatus,
    SearchFilterOptions,
    SearchFilters,
    SearchItem,
    SearchPagination,
    SearchSuggestion,
    UnifiedSearchResponse,
)
from app.search.utils.scoring import (
    MAX_QUERY_LENGTH,
    combine_scores,
    recency_score,
    sanitize_text,
    tokenize_query,
)

logger = logging.getLogger(__name__)

MAX_PAGE = 1000
MAX_LIMIT = 50
DEFAULT_LIMIT = 20
PROVIDER_SOFT_BUDGET_SECONDS = 4.0

_SORT_LABELS = {
    "relevance": "Best match",
    "newest": "Newest first",
    "oldest": "Oldest first",
}

_TYPE_ALIASES = {
    "all": "",
    "task": "tasks",
    "note": "notes",
    "document": "documents",
    "conversation": "conversations",
    "memory": "memories",
    "knowledge": "knowledge",
}


@dataclass
class _ScoredHit:
    hit: ProviderHit
    score: float


class UnifiedSearchService:
    """Single entry point for workspace search."""

    def __init__(
        self,
        providers: Optional[Sequence[SearchProvider]] = None,
        history: Optional[SearchHistoryService] = None,
    ):
        self.providers: List[SearchProvider] = (
            list(providers) if providers is not None else default_providers()
        )
        self._by_type: Dict[str, SearchProvider] = {
            provider.resource_type: provider for provider in self.providers
        }
        self.history = history or search_history_service

    # ------------------------------------------------------------------
    # Validation / metadata
    # ------------------------------------------------------------------
    @property
    def supported_resource_types(self) -> List[str]:
        return list(self._by_type.keys())

    def normalize_resource_types(self, resource_types: Optional[Iterable[str]]) -> List[str]:
        """Validate and normalize requested types (singular aliases allowed)."""
        if not resource_types:
            return []

        normalized: List[str] = []
        unknown: List[str] = []
        for raw in resource_types:
            if raw is None:
                continue
            value = str(raw).strip().lower()
            if not value:
                continue
            value = _TYPE_ALIASES.get(value, value)
            if not value:
                continue
            if value not in self._by_type:
                unknown.append(str(raw))
            elif value not in normalized:
                normalized.append(value)

        if unknown:
            supported = ", ".join(self.supported_resource_types)
            raise ValueError(
                f"Unsupported resource type(s): {', '.join(sorted(set(unknown)))}. "
                f"Supported types: {supported}."
            )
        return normalized

    def get_filter_options(self) -> SearchFilterOptions:
        from app.search.search_models import ResourceTypeInfo, SortInfo

        types = [
            ResourceTypeInfo(
                value=provider.resource_type,
                label=provider.display_name,
                available=provider.available(),
                reason=None if provider.available() else provider.unavailable_reason(),
            )
            for provider in self.providers
        ]
        return SearchFilterOptions(
            resource_types=types,
            sorts=[SortInfo(value=value, label=label) for value, label in _SORT_LABELS.items()],
            semantic_available=any(
                provider.resource_type == "knowledge" and provider.available()
                for provider in self.providers
            ),
            max_limit=MAX_LIMIT,
            max_query_length=MAX_QUERY_LENGTH,
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(
        self,
        db: Session,
        user_id: int,
        query: str,
        resource_types: Optional[Sequence[str]] = None,
        sort: str = "relevance",
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        semantic: bool = False,
        record_history: bool = True,
    ) -> UnifiedSearchResponse:
        """Run a unified search for one authenticated user."""
        started = time.perf_counter()

        if user_id is None:
            raise ValueError("An authenticated user id is required.")

        text = sanitize_text(query or "", MAX_QUERY_LENGTH)
        selected_types = self.normalize_resource_types(resource_types)

        filters = SearchFilters(
            resource_types=selected_types,
            date_from=date_from,
            date_to=date_to,
            sort=sort,  # type: ignore[arg-type]
            semantic=bool(semantic),
        )

        page = max(1, min(int(page or 1), MAX_PAGE))
        limit = max(1, min(int(limit or DEFAULT_LIMIT), MAX_LIMIT))

        applied_filters = AppliedSearchFilters(
            resource_types=selected_types or self.supported_resource_types,
            date_from=filters.date_from,
            date_to=filters.date_to,
            sort=filters.sort,
            semantic=filters.semantic,
        )

        terms = tokenize_query(text)
        provider_query = ProviderQuery(
            text=text,
            terms=terms,
            date_from=filters.date_from,
            date_to=filters.date_to,
            semantic=filters.semantic,
        )

        provider_statuses: List[ProviderStatus] = []
        collected: List[ProviderHit] = []

        if not text or not terms:
            response = self._build_response(
                text=text,
                filters=applied_filters,
                hits=[],
                page=page,
                limit=limit,
                providers=self._skipped_statuses(selected_types, "Empty query."),
                started=started,
            )
            if record_history and text:
                self.history.record(db, user_id, text, selected_types, 0)
            return response

        target_providers = [
            provider
            for provider in self.providers
            if not selected_types or provider.resource_type in selected_types
        ]
        candidate_limit = min(max(limit * 3, 20), 100)
        budget_exhausted = False

        for provider in target_providers:
            if not provider.available():
                provider_statuses.append(
                    ProviderStatus(
                        resource_type=provider.resource_type,
                        display_name=provider.display_name,
                        status="disabled",
                        error=provider.unavailable_reason() or "Provider unavailable.",
                    )
                )
                continue

            skip_reason = provider.skip_reason(provider_query)
            if skip_reason:
                provider_statuses.append(
                    ProviderStatus(
                        resource_type=provider.resource_type,
                        display_name=provider.display_name,
                        status="disabled",
                        error=skip_reason,
                    )
                )
                continue

            if budget_exhausted:
                provider_statuses.append(
                    ProviderStatus(
                        resource_type=provider.resource_type,
                        display_name=provider.display_name,
                        status="skipped",
                        error="Search time budget exhausted.",
                    )
                )
                continue

            provider_started = time.perf_counter()
            try:
                hits = provider.search(db, user_id, provider_query, candidate_limit)
                duration_ms = round((time.perf_counter() - provider_started) * 1000, 2)
                collected.extend(hits)
                provider_statuses.append(
                    ProviderStatus(
                        resource_type=provider.resource_type,
                        display_name=provider.display_name,
                        status="ok",
                        result_count=len(hits),
                        duration_ms=duration_ms,
                    )
                )
            except Exception:
                duration_ms = round((time.perf_counter() - provider_started) * 1000, 2)
                # Log the real error server-side; never leak internals to clients.
                logger.exception(
                    "Search provider '%s' failed for user %s", provider.resource_type, user_id
                )
                provider_statuses.append(
                    ProviderStatus(
                        resource_type=provider.resource_type,
                        display_name=provider.display_name,
                        status="error",
                        duration_ms=duration_ms,
                        error="Provider failed. Other results are unaffected.",
                    )
                )

            if (time.perf_counter() - started) > PROVIDER_SOFT_BUDGET_SECONDS:
                budget_exhausted = True

        scored = self._rank_and_dedupe(collected, filters.sort)
        response = self._build_response(
            text=text,
            filters=applied_filters,
            hits=scored,
            page=page,
            limit=limit,
            providers=provider_statuses,
            started=started,
        )

        if record_history:
            self.history.record(db, user_id, text, selected_types, response.pagination.total)

        return response

    # ------------------------------------------------------------------
    # Suggestions
    # ------------------------------------------------------------------
    def suggestions(
        self,
        db: Session,
        user_id: int,
        query: str,
        limit: int = 8,
    ) -> List[SearchSuggestion]:
        """Cheap suggestions from history and bounded title lookups."""
        limit = max(1, min(int(limit or 8), 10))
        text = sanitize_text(query or "", MAX_QUERY_LENGTH)
        terms = tokenize_query(text)
        lowered = text.lower()
        suggestions: List[SearchSuggestion] = []
        seen: set[str] = set()

        def add(suggestion: SearchSuggestion) -> bool:
            key = suggestion.text.strip().lower()
            if not key or key in seen:
                return False
            seen.add(key)
            suggestions.append(suggestion)
            return len(suggestions) >= limit

        try:
            for item in self.history.list(db, user_id, limit=5):
                if lowered and lowered not in item.query.lower():
                    continue
                if add(
                    SearchSuggestion(
                        text=item.query,
                        kind="history",
                    )
                ):
                    return suggestions
        except Exception:
            logger.exception("Failed to read search history for suggestions (user %s)", user_id)

        if not terms:
            return suggestions

        for provider in self.providers:
            if len(suggestions) >= limit:
                break
            if not provider.available():
                continue
            try:
                rows = provider.suggest(
                    db=db,
                    user_id=user_id,
                    query=text,
                    terms=terms,
                    limit=2,
                )
            except Exception:
                logger.exception(
                    "Suggestion provider '%s' failed for user %s",
                    provider.resource_type,
                    user_id,
                )
                continue

            for row in rows:
                if add(
                    SearchSuggestion(
                        text=str(row.get("text", "")).strip(),
                        kind="resource",
                        resource_type=row.get("resource_type"),
                        resource_id=row.get("resource_id"),
                        url=row.get("url"),
                    )
                ):
                    return suggestions

        return suggestions

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _skipped_statuses(
        self, selected_types: Sequence[str], reason: str
    ) -> List[ProviderStatus]:
        return [
            ProviderStatus(
                resource_type=provider.resource_type,
                display_name=provider.display_name,
                status="skipped",
                error=reason,
            )
            for provider in self.providers
            if not selected_types or provider.resource_type in selected_types
        ]

    def _rank_and_dedupe(self, hits: Iterable[ProviderHit], sort: str) -> List[_ScoredHit]:
        best: Dict[str, _ScoredHit] = {}

        for hit in hits:
            if hit.lexical_score <= 0.0 and not (hit.semantic_score and hit.semantic_score > 0):
                continue

            score = combine_scores(
                hit.lexical_score,
                hit.semantic_score,
                recency_score(hit.updated_at or hit.created_at),
            )
            key = hit.dedupe_key
            existing = best.get(key)
            if existing is None or score > existing.score:
                best[key] = _ScoredHit(hit=hit, score=score)

        scored = list(best.values())

        if sort == "newest":
            scored.sort(
                key=lambda item: (
                    item.hit.updated_at or item.hit.created_at or datetime.min,
                    item.score,
                ),
                reverse=True,
            )
        elif sort == "oldest":
            scored.sort(
                key=lambda item: (
                    item.hit.updated_at or item.hit.created_at or datetime.max,
                    -item.score,
                )
            )
        else:
            scored.sort(
                key=lambda item: (
                    item.score,
                    item.hit.updated_at or item.hit.created_at or datetime.min,
                ),
                reverse=True,
            )
        return scored

    def _build_response(
        self,
        *,
        text: str,
        filters: AppliedSearchFilters,
        hits: Sequence[_ScoredHit],
        page: int,
        limit: int,
        providers: Sequence[ProviderStatus],
        started: float,
    ) -> UnifiedSearchResponse:
        total = len(hits)
        total_pages = math.ceil(total / limit) if total else 0
        offset = (page - 1) * limit
        page_hits = hits[offset : offset + limit]

        items = [
            SearchItem(
                id=scored.hit.dedupe_key,
                resource_id=scored.hit.resource_id,
                resource_type=scored.hit.resource_type,
                title=scored.hit.title,
                snippet=scored.hit.snippet,
                url=scored.hit.url,
                matched_fields=scored.hit.matched_fields,
                created_at=scored.hit.created_at,
                updated_at=scored.hit.updated_at,
                relevance_score=round(scored.score, 4),
                metadata=scored.hit.metadata,
            )
            for scored in page_hits
        ]

        return UnifiedSearchResponse(
            query=text,
            items=items,
            pagination=SearchPagination(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1 and total > 0,
            ),
            filters=filters,
            providers=list(providers),
            took_ms=round((time.perf_counter() - started) * 1000, 2),
        )


unified_search_service = UnifiedSearchService()
