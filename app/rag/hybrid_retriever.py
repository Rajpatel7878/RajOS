import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.rag.vector_store import knowledge_vector_store
from app.rag.rag_config import rag_config


class HybridRetriever:
    """
    Hybrid Retrieval Engine combining semantic vector search + SQL keyword matching
    with deterministic reranking and relevance thresholding.
    """

    @classmethod
    def keyword_search(
        cls,
        db: Session,
        user_id: int,
        query_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Searches ready documents in SQL DB for keyword & exact phrase matches."""
        terms = [t.strip().lower() for t in re.split(r'\s+', query_text) if len(t.strip()) > 2]
        if not terms:
            return []

        user_docs = db.query(Document).filter(
            Document.user_id == user_id,
            Document.status == "ready"
        ).all()

        keyword_hits = []
        for doc in user_docs:
            text_lower = (doc.content or "").lower()
            title_lower = (doc.filename or "").lower() + " " + (doc.title or "").lower()

            hit_count = 0
            for term in terms:
                if term in text_lower or term in title_lower:
                    hit_count += text_lower.count(term) + title_lower.count(term) * 2

            if hit_count > 0:
                # Find matching paragraph snippet
                snippets = text_lower.split("\n\n")
                best_snippet = doc.content[:400]
                for snip in snippets:
                    if any(t in snip for t in terms):
                        best_snippet = snip.strip()[:400]
                        break

                density_score = min(1.0, hit_count / (len(terms) * 3.0))
                keyword_hits.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "title": doc.title or doc.filename,
                    "chunk_id": f"doc_{doc.id}_kw",
                    "content": best_snippet,
                    "keyword_score": density_score,
                    "heading": "Keyword Match"
                })

        keyword_hits.sort(key=lambda x: x["keyword_score"], reverse=True)
        return keyword_hits[:limit]

    @classmethod
    def search(
        cls,
        db: Session,
        user_id: int,
        query_text: str,
        limit: int = rag_config.RAG_TOP_K,
        candidate_limit: int = rag_config.RAG_CANDIDATE_LIMIT,
        relevance_threshold: float = rag_config.RAG_RELEVANCE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search (vector + keyword), fuses & reranks results,
        and applies relevance thresholding.
        """
        if not query_text or not query_text.strip():
            return []

        # 1. Semantic Vector Search
        vector_candidates = knowledge_vector_store.search(
            user_id=user_id,
            query_text=query_text,
            limit=candidate_limit
        )

        # 2. Keyword Search
        keyword_candidates = cls.keyword_search(
            db=db,
            user_id=user_id,
            query_text=query_text,
            limit=candidate_limit
        )

        # 3. Hybrid Fusion & Reranking
        candidate_map: Dict[str, Dict[str, Any]] = {}

        for hit in vector_candidates:
            cid = hit["chunk_id"]
            sim = hit.get("similarity", 0.0)
            candidate_map[cid] = {
                "chunk_id": cid,
                "document_id": hit["document_id"],
                "filename": hit.get("filename", ""),
                "heading": hit.get("heading", "General"),
                "content": hit.get("content", ""),
                "semantic_score": sim,
                "keyword_score": 0.0,
                "score": sim * 0.70
            }

        for kw in keyword_candidates:
            cid = kw["chunk_id"]
            kw_score = kw.get("keyword_score", 0.0)
            if cid in candidate_map:
                candidate_map[cid]["keyword_score"] = kw_score
                candidate_map[cid]["score"] = (candidate_map[cid]["semantic_score"] * 0.65) + (kw_score * 0.35)
            else:
                candidate_map[cid] = {
                    "chunk_id": cid,
                    "document_id": kw["document_id"],
                    "filename": kw.get("filename", ""),
                    "heading": kw.get("heading", "Keyword Match"),
                    "content": kw.get("content", ""),
                    "semantic_score": 0.0,
                    "keyword_score": kw_score,
                    "score": kw_score * 0.50
                }

        # 4. Filter by Relevance Threshold
        ranked_hits = list(candidate_map.values())
        ranked_hits.sort(key=lambda x: x["score"], reverse=True)

        filtered_hits = [hit for hit in ranked_hits if hit["score"] >= relevance_threshold]

        return filtered_hits[:limit]


hybrid_retriever = HybridRetriever()
