"""Knowledge base chunk provider.

This provider deliberately reuses the existing RAG hybrid retriever
(``knowledge_service.search_knowledge``) instead of creating a second vector
index.  It is opt-in: ordinary workspace search is lexical and deterministic,
and semantic retrieval only runs when the caller asks for it.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.document import Document
from app.rag.knowledge_service import knowledge_service
from app.rag.rag_config import rag_config
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider
from app.search.utils.scoring import matched_fields, score_lexical

logger = logging.getLogger(__name__)


class KnowledgeSearchProvider(SearchProvider):
    resource_type = "knowledge"
    display_name = "Knowledge base"
    default_url = "/documents"

    def available(self) -> bool:
        return bool(rag_config.RAG_ENABLED)

    def unavailable_reason(self) -> str:
        return "Knowledge base retrieval is disabled (RAG_ENABLED=false)."

    def skip_reason(self, query: ProviderQuery):
        if not query.semantic:
            return "Semantic retrieval was not requested for this query."
        return None

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        if not query.semantic:
            return []
        if not query.text.strip():
            return []

        chunk_limit = min(max(limit * 2, 5), rag_config.RAG_CANDIDATE_LIMIT, 20)
        try:
            results = knowledge_service.search_knowledge(
                db=db,
                user_id=user_id,
                query_text=query.text,
                limit=chunk_limit,
            )
        except Exception:
            # Propagated to the service layer, which reports this provider as
            # failed while keeping lexical results from other providers intact.
            logger.exception("Knowledge semantic retrieval failed for user %s", user_id)
            raise

        if not results:
            return []

        document_ids = {
            int(hit.get("document_id"))
            for hit in results
            if hit.get("document_id") is not None
        }

        # Defense in depth: only keep hits whose document is owned by this user
        # and still ready.  Also fetch timestamps in one query (no N+1).
        owned: Dict[int, Document] = {}
        if document_ids:
            rows = (
                db.query(Document)
                .filter(
                    Document.user_id == user_id,
                    Document.status == "ready",
                    Document.id.in_(document_ids),
                )
                .all()
            )
            owned = {doc.id: doc for doc in rows}

        hits: List[ProviderHit] = []
        for result in results:
            try:
                document_id = int(result.get("document_id"))
            except (TypeError, ValueError):
                continue

            document = owned.get(document_id)
            if document is None:
                continue
            if query.date_from is not None and document.updated_at < query.date_from:
                continue
            if query.date_to is not None and document.updated_at > query.date_to:
                continue

            title = result.get("title") or document.title or document.filename
            content = result.get("content") or ""
            semantic = _clamp(float(result.get("score", 0.0)))
            chunk_id = str(result.get("chunk_id") or f"doc_{document_id}")
            heading = result.get("heading") or "General"

            lexical = score_lexical(title, [content], query.text)
            if lexical.combined <= 0.0 and semantic <= 0.0:
                continue

            hits.append(
                ProviderHit(
                    resource_type=self.resource_type,
                    resource_id=str(document_id),
                    title=f"{title} · {heading}" if heading and heading != "General" else (title or "Document"),
                    snippet=content[:600].strip(),
                    url=self.default_url,
                    matched_fields=matched_fields(
                        {"title": title, "heading": heading, "content": content},
                        query.terms,
                    )
                    or ["semantic"],
                    created_at=document.created_at,
                    updated_at=document.updated_at,
                    lexical_score=lexical.combined,
                    semantic_score=semantic,
                    metadata={
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "heading": heading,
                        "filename": document.filename,
                    },
                )
            )

        hits.sort(key=lambda hit: (hit.semantic_score or 0.0), reverse=True)
        return hits

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        # Document titles are already suggested by the document provider;
        # avoid duplicate/expensive vector lookups for suggestions.
        return []


def _clamp(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 4)
