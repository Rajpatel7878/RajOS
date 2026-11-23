"""Document (knowledge base file) search provider."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.document import Document
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider, contains_any


class DocumentSearchProvider(SearchProvider):
    """Searches uploaded document rows.

    Only ``ready`` documents are searchable: processing or failed documents do
    not have a complete, trustworthy text representation yet.
    """

    resource_type = "documents"
    display_name = "Documents"
    default_url = "/documents"

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        condition = contains_any([Document.title, Document.filename, Document.content], query.terms)
        if condition is None:
            return []

        q = db.query(Document).filter(
            Document.user_id == user_id,
            Document.status == "ready",
            condition,
        )
        if query.date_from is not None:
            q = q.filter(Document.updated_at >= query.date_from)
        if query.date_to is not None:
            q = q.filter(Document.updated_at <= query.date_to)

        documents = (
            q.order_by(Document.updated_at.desc(), Document.id.desc())
            .limit(min(limit, self.candidate_limit))
            .all()
        )

        hits: List[ProviderHit] = []
        for doc in documents:
            title = doc.title or doc.filename
            hit = self.make_hit(
                resource_id=doc.id,
                title=title,
                snippet_source=doc.content,
                query=query,
                fields={"title": title, "filename": doc.filename, "content": doc.content},
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                metadata={
                    "filename": doc.filename,
                    "mime_type": doc.mime_type,
                },
            )
            if hit.matched_fields:
                hits.append(hit)
        return hits

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        condition = contains_any([Document.title, Document.filename], terms)
        if condition is None:
            return []
        rows = (
            db.query(Document.id, Document.title, Document.filename)
            .filter(
                Document.user_id == user_id,
                Document.status == "ready",
                condition,
            )
            .order_by(Document.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "text": row.title or row.filename,
                "kind": "resource",
                "resource_type": self.resource_type,
                "resource_id": str(row.id),
                "url": self.default_url,
            }
            for row in rows
        ]
