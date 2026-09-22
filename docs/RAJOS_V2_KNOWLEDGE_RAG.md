# RajOS V2 Phase 5 — Knowledge Base & RAG 2.0 Architectural Documentation

## 1. Executive Summary
RajOS V2 Phase 5 (Knowledge Base & RAG 2.0) transforms RajOS from basic document storage into an enterprise-grade Knowledge Base and Retrieval-Augmented Generation (RAG) system. It features intelligent text normalization and paragraph/section chunking with configurable overlap, centralized vector embeddings, hybrid vector + keyword search fusion, deterministic reranking, relevance threshold filtering, strict multi-user data isolation, prompt injection defense, and grounded AI responses with source citations.

---

## 2. Architecture & Data Flow

```text
User / API / Frontend UI
           ↓
   Document Upload / Edit
           ↓
   DocumentService (Ingestion & Lifecycle Management)
           ↓
   DocumentProcessor (Text Normalization, Paragraph Chunking, Overlap)
           ↓
   EmbeddingService (Centralized SentenceTransformer / Offline Fallback)
           ↓
   KnowledgeVectorStore (ChromaDB `rajOS_knowledge` Collection with user_id Scoping)
           ↓
   HybridRetriever (Semantic Vector Search + SQL Keyword Match Fusion & Reranking)
           ↓
   Relevance Threshold Filtering (Rejects noise below score threshold 0.35)
           ↓
   ContextBuilder (Token Budget Capping + Prompt Injection Defense Tagging)
           ↓
   AI Core / LLM Prompt (Grounded Response + Source Citations)
```

---

## 3. Key Components & Implementation Details

### 3.1 Extended Document ORM Model (`app/models/document.py`)
- `id`: Primary key
- `user_id`: Foreign key to `users.id`
- `filename`: Original file name
- `title`: Document display title
- `content`: Original full text content
- `mime_type`: `text/plain | text/markdown | application/json | text/csv`
- `file_size`: Integer byte count
- `status`: `uploaded | processing | ready | failed | archived`
- `processed_at`: Ingestion completion timestamp
- `error_message`: Text diagnostics for processing errors
- `metadata_json`: Structured JSON containing metadata (chunk counts, headings)
- `created_at` / `updated_at`: Timestamps

### 3.2 Alembic Migration (`alembic/versions/2a1a5f704789_add_rag_2_fields.py`)
Safe non-destructive schema migration with `server_default` constraints for SQLite database compatibility.

### 3.3 Centralized RAG Configuration (`app/rag/rag_config.py`)
Configurable parameters overridable via environment variables:
- `RAG_ENABLED`: `True`
- `RAG_CHUNK_SIZE`: `500` words
- `RAG_CHUNK_OVERLAP`: `80` words
- `RAG_TOP_K`: `5` chunks
- `RAG_CANDIDATE_LIMIT`: `15` candidate chunks
- `RAG_RELEVANCE_THRESHOLD`: `0.35` min score
- `RAG_CONTEXT_TOKEN_BUDGET`: `2000` tokens
- `RAG_HYBRID_SEARCH_ENABLED`: `True`

### 3.4 Intelligent Document Processing (`app/rag/document_processor.py`)
- Normalizes line endings (`\r\n` -> `\n`) and collapses excessive blank lines.
- Splits content into semantically coherent paragraph blocks while respecting chunk limits and chunk overlap.
- Extracts Markdown headings and structural tags for source reference context.

### 3.5 Vector Store & Security Isolation (`app/rag/vector_store.py`)
- Collection: `rajOS_knowledge` in ChromaDB.
- Enforces strict `user_id` metadata filtering on all vector additions, queries, and deletions (`where={"user_id": user_id}`).
- Ephemeral in-memory client mode during pytest runs (`DATABASE_URL=sqlite:///:memory:`).

### 3.6 Hybrid Retrieval & Reranking (`app/rag/hybrid_retriever.py`)
- Combines candidate results from Semantic Vector Similarity Search and SQL Keyword Density Matching.
- Computes hybrid rerank score: `0.65 * semantic_similarity + 0.35 * keyword_density_score`.
- Filters out weak candidates below `RAG_RELEVANCE_THRESHOLD` (0.35) to prevent hallucinations.

### 3.7 Knowledge Service & Prompt Injection Defense (`app/rag/knowledge_service.py`)
- Orchestrates document ingestion, updates, deletions, hybrid search, and context formatting.
- **Prompt Injection Defense**: Wraps retrieved document text inside `<UNTRUSTED_KNOWLEDGE_DOCUMENT>` tags and instructs the LLM to treat document text strictly as reference data without executing embedded instructions.
- **Vector Purging**: Automatically purges old vector chunks from ChromaDB whenever a document is updated or deleted.

### 3.8 Context Integration & Chat Router (`app/services/context_builder.py`, `app/routers/chat.py`, `app/services/ai_service.py`)
- Wires grounded knowledge context into `ContextBuilder` alongside short-term conversation history and long-term memory.
- Returns `sources` array in `ChatResponse` payload for frontend citation displays.

### 3.9 REST API Endpoints (`app/routers/documents.py`)
- `GET /documents`: List user documents with filter options
- `GET /documents/{id}`: Retrieve document details
- `POST /documents/`: Upload, chunk, embed, and index document
- `PUT /documents/{id}`: Update title/content and re-index vector chunks
- `DELETE /documents/{id}`: Delete document and purge vector chunks
- `POST /documents/search`: Execute hybrid knowledge search
- `GET /documents/stats`: Retrieve Knowledge Base statistics

### 3.10 Frontend Knowledge Base & Documents UI (`Frontend/app/documents/page.tsx`, `Frontend/app/knowledge/page.tsx`, `Frontend/services/api/documents.ts`)
- Client API service `documents.ts`.
- Real document upload with file drop zone & format support (.txt, .md, .csv, .json).
- Status badges (`Ready`, `Processing`, `Failed`), storage size indicators, and content viewer drawer.
- Hybrid search interface with relevance progress bars and source citations.

---

## 4. Security Audit & Isolation Verification
1. **User Data Isolation**: Application-level authorization + ChromaDB metadata filtering (`where={"user_id": user_id}`) prevents User B from seeing, searching, or deleting User A's documents or vector chunks.
2. **Vector Purge Integrity**: Document deletion and content updates purge stale vector chunks immediately.
3. **Prompt Injection Protection**: Document text is isolated in `<UNTRUSTED_KNOWLEDGE_DOCUMENT>` tags in LLM context.

---

## 5. Automated Test Verification Results
- **Backend Test Suite (pytest)**: All **43/43 tests passed (100%)** including 8 dedicated Phase 5 tests in `tests/test_knowledge_rag.py`.
- **Frontend Typecheck (tsc)**: `tsc --noEmit` passed with 0 errors.
