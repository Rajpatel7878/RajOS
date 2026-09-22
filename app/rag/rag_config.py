import os


class RAGConfig:
    """
    Centralized configuration for RajOS Knowledge Base & RAG 2.0.
    Values can be overridden via environment variables.
    """

    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "true").lower() == "true"
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_CANDIDATE_LIMIT: int = int(os.getenv("RAG_CANDIDATE_LIMIT", "15"))
    RAG_RELEVANCE_THRESHOLD: float = float(os.getenv("RAG_RELEVANCE_THRESHOLD", "0.35"))
    RAG_CONTEXT_TOKEN_BUDGET: int = int(os.getenv("RAG_CONTEXT_TOKEN_BUDGET", "2000"))
    RAG_HYBRID_SEARCH_ENABLED: bool = os.getenv("RAG_HYBRID_SEARCH_ENABLED", "true").lower() == "true"
    RAG_MAX_FILE_SIZE_BYTES: int = int(os.getenv("RAG_MAX_FILE_SIZE_BYTES", "25000000"))  # 25 MB max


rag_config = RAGConfig()
