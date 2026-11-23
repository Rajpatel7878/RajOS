"""Provider contract for RajOS unified search.

Each resource type is searched by an independent provider.  Providers are
synchronous, receive an already-authenticated ``user_id`` and are responsible
for scoping every query to that user.  A provider failure must never take down
the whole search: :class:`app.search.unified_search_service.UnifiedSearchService`
catches and reports failures per provider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.search.utils.scoring import build_snippet, matched_fields, score_lexical


@dataclass(frozen=True)
class ProviderQuery:
    """Normalized query passed to every provider."""

    text: str
    terms: List[str]
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    semantic: bool = False


@dataclass
class ProviderHit:
    """One resource returned by a provider, before global ranking."""

    resource_type: str
    resource_id: str
    title: str
    snippet: str
    url: Optional[str]
    matched_fields: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lexical_score: float = 0.0
    semantic_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def dedupe_key(self) -> str:
        """Stable identity used to remove duplicate results.

        Knowledge chunks are separately addressable passages of the same
        document, so a chunk id (when present) participates in the key.
        """
        chunk_id = self.metadata.get("chunk_id")
        if chunk_id:
            return f"{self.resource_type}:{chunk_id}"
        return f"{self.resource_type}:{self.resource_id}"


def contains_any(columns, terms: Sequence[str]):
    """Build a parameterized ``OR`` of case-insensitive contains clauses.

    Terms are sanitized by ``tokenize_query`` (word characters only), and
    SQLAlchemy binds them as parameters, so no user text reaches SQL directly.
    """
    safe_terms = [term for term in terms if term]
    if not safe_terms or not columns:
        return None
    return or_(*[column.ilike(f"%{term}%") for column in columns for term in safe_terms])


class SearchProvider(ABC):
    """Base class for a single resource-type search provider."""

    resource_type: str = ""
    display_name: str = ""
    default_url: Optional[str] = None
    candidate_limit: int = 100

    def available(self) -> bool:
        """Return False when the underlying feature is not configured."""
        return True

    def unavailable_reason(self) -> Optional[str]:
        """Safe, human-readable reason shown when ``available()`` is False."""
        return None

    def skip_reason(self, query: ProviderQuery) -> Optional[str]:
        """Reason this provider opts out of a specific query, if any."""
        return None

    @abstractmethod
    def search(
        self,
        db: Session,
        user_id: int,
        query: ProviderQuery,
        limit: int,
    ) -> List[ProviderHit]:
        """Search this resource type for one authenticated user."""

    def suggest(
        self,
        db: Session,
        user_id: int,
        query: str,
        terms: Sequence[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Return optional title suggestions. Defaults to none."""
        return []

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def make_hit(
        self,
        *,
        resource_id: Any,
        title: Optional[str],
        snippet_source: Optional[str],
        query: ProviderQuery,
        fields: Dict[str, Optional[str]],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        semantic_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
    ) -> ProviderHit:
        """Create a hit; see class docstring for scoping expectations."""
        """Build a scored hit with consistent snippets and matched fields."""
        lexical = score_lexical(title, fields.values(), query.text)
        return ProviderHit(
            resource_type=self.resource_type,
            resource_id=str(resource_id),
            title=(title or "Untitled").strip(),
            snippet=build_snippet(snippet_source or title, query.text, query.terms),
            url=url if url is not None else self.default_url,
            matched_fields=matched_fields(fields, query.terms),
            created_at=created_at,
            updated_at=updated_at,
            lexical_score=lexical.combined,
            semantic_score=semantic_score,
            metadata=metadata or {},
        )
