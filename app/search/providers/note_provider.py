"""Note search provider."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.note import Note
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider, contains_any


class NoteSearchProvider(SearchProvider):
    resource_type = "notes"
    display_name = "Notes"
    default_url = "/notes"

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        condition = contains_any([Note.title, Note.content], query.terms)
        if condition is None:
            return []

        q = db.query(Note).filter(Note.user_id == user_id, condition)
        if query.date_from is not None:
            q = q.filter(Note.updated_at >= query.date_from)
        if query.date_to is not None:
            q = q.filter(Note.updated_at <= query.date_to)

        notes = (
            q.order_by(Note.updated_at.desc(), Note.id.desc())
            .limit(min(limit, self.candidate_limit))
            .all()
        )

        hits: List[ProviderHit] = []
        for note in notes:
            hit = self.make_hit(
                resource_id=note.id,
                title=note.title,
                snippet_source=note.content,
                query=query,
                fields={"title": note.title, "content": note.content},
                created_at=note.created_at,
                updated_at=note.updated_at,
            )
            if hit.matched_fields:
                hits.append(hit)
        return hits

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        condition = contains_any([Note.title], terms)
        if condition is None:
            return []
        rows = (
            db.query(Note.id, Note.title)
            .filter(Note.user_id == user_id, condition)
            .order_by(Note.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "text": row.title,
                "kind": "resource",
                "resource_type": self.resource_type,
                "resource_id": str(row.id),
                "url": self.default_url,
            }
            for row in rows
        ]
