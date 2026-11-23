"""User-scoped search history."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.search_history import SearchHistory
from app.search.search_models import SearchHistoryItem
from app.search.utils.scoring import MAX_QUERY_LENGTH, sanitize_text

logger = logging.getLogger(__name__)


class SearchHistoryService:
    """Stores and reads search history for one authenticated user at a time."""

    def record(
        self,
        db: Session,
        user_id: int,
        query: str,
        resource_types: Sequence[str],
        result_count: int = 0,
    ) -> None:
        """Record a non-empty query, replacing an identical earlier entry."""
        cleaned = sanitize_text(query, MAX_QUERY_LENGTH)
        if not cleaned:
            return

        try:
            db.query(SearchHistory).filter(
                SearchHistory.user_id == user_id,
                func.lower(SearchHistory.query) == cleaned.lower(),
            ).delete(synchronize_session=False)

            db.add(
                SearchHistory(
                    user_id=user_id,
                    query=cleaned,
                    search_type=",".join(resource_types) if resource_types else "all",
                    resource_types=",".join(resource_types) if resource_types else "all",
                    result_count=max(0, int(result_count)),
                    searched_at=datetime.utcnow(),
                )
            )
            db.commit()
        except Exception:
            # History must never break a search response.
            db.rollback()
            logger.exception("Failed to record search history for user %s", user_id)

    def list(self, db: Session, user_id: int, limit: int = 10) -> List[SearchHistoryItem]:
        limit = max(1, min(int(limit), 50))
        rows = (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.searched_at.desc(), SearchHistory.id.desc())
            .limit(limit * 3)
            .all()
        )

        items: List[SearchHistoryItem] = []
        seen: set[str] = set()
        for row in rows:
            key = (row.query or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)

            resource_types = [
                value
                for value in (row.resource_types or row.search_type or "").split(",")
                if value and value != "all"
            ]
            items.append(
                SearchHistoryItem(
                    id=row.id,
                    query=row.query,
                    resource_types=resource_types,
                    result_count=row.result_count or 0,
                    searched_at=row.searched_at or datetime.utcnow(),
                )
            )
            if len(items) >= limit:
                break
        return items

    def clear(self, db: Session, user_id: int) -> int:
        deleted = (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .delete(synchronize_session=False)
        )
        db.commit()
        return int(deleted or 0)


search_history_service = SearchHistoryService()
