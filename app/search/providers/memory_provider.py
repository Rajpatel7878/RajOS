"""Memory search provider."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider, contains_any


class MemorySearchProvider(SearchProvider):
    resource_type = "memories"
    display_name = "Memories"
    default_url = "/memory"

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        condition = contains_any([Memory.key, Memory.value, Memory.content], query.terms)
        if condition is None:
            return []

        q = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "active",
            condition,
        )
        if query.date_from is not None:
            q = q.filter(Memory.updated_at >= query.date_from)
        if query.date_to is not None:
            q = q.filter(Memory.updated_at <= query.date_to)

        memories = (
            q.order_by(Memory.updated_at.desc(), Memory.id.desc())
            .limit(min(limit, self.candidate_limit))
            .all()
        )

        hits: List[ProviderHit] = []
        for memory in memories:
            snippet_source = memory.value
            if memory.content and memory.content not in memory.value:
                snippet_source = f"{memory.value} — {memory.content}"
            hit = self.make_hit(
                resource_id=memory.id,
                title=memory.key,
                snippet_source=snippet_source,
                query=query,
                fields={
                    "title": memory.key,
                    "value": memory.value,
                    "content": memory.content,
                },
                created_at=memory.created_at,
                updated_at=memory.updated_at,
                metadata={
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                },
            )
            if hit.matched_fields:
                hits.append(hit)
        return hits

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        condition = contains_any([Memory.key], terms)
        if condition is None:
            return []
        rows = (
            db.query(Memory.id, Memory.key)
            .filter(
                Memory.user_id == user_id,
                Memory.status == "active",
                condition,
            )
            .order_by(Memory.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "text": row.key,
                "kind": "resource",
                "resource_type": self.resource_type,
                "resource_id": str(row.id),
                "url": self.default_url,
            }
            for row in rows
        ]
