# RajOS V2 Phase 4 — Memory 2.0 Architectural Documentation

## Executive Overview
RajOS V2 Phase 4 (Memory 2.0) upgrades RajOS from legacy key-value storage into a long-term memory engine featuring hybrid vector retrieval, explicit and inferred memory extraction, secret filtering, conflict resolution deduplication, multi-user isolation, and failure-isolated context injection.

---

## Key Modules & Components

### 1. Database Model (`app/models/memory.py`)
Extended the `Memory` ORM schema with high-granularity metadata:
- `key`: Memory title / topic indicator
- `value`: Memory content statement
- `content`: Detailed optional contextual background
- `memory_type`: `preference | goal | project | instruction | fact`
- `source`: `explicit_user | inferred_llm | system`
- `confidence`: `low | medium | high`
- `importance`: `low | medium | high | critical`
- `status`: `active | deleted | archived`
- `created_at` / `updated_at`: Timestamps
- `last_accessed_at` / `access_count`: Usage telemetry

### 2. Alembic Migration (`alembic/versions/633a3a32197a_add_memory_2_fields.py`)
Provides safe non-destructive migration for existing SQLite databases with `server_default` constraints.

### 3. Vector Storage (`app/memory/memory_vector_store.py`)
- Manages ChromaDB collection `rajOS_memories`.
- Implements `MemoryVectorStore` with strict `user_id` metadata filtering on all vector queries.
- Dynamically uses ephemeral in-memory client during pytest test execution for complete test isolation.

### 4. Secret & Noise Filter (`app/memory/memory_validator.py`)
- Detects and rejects API keys, passwords, bearer tokens, connection strings, SSNs, and credit card numbers.
- Suppresses conversational noise and transient queries ("what time is it", "hello", "run command").

### 5. Deduplication & Conflict Resolution (`app/memory/memory_deduplicator.py`)
- Performs exact match checking to prevent identical memory creation.
- Resolves topic/key conflicts by updating existing memories rather than creating duplicates.
- Uses semantic vector similarity thresholds (>0.88) to consolidate related memories.

### 6. Service Orchestration (`app/memory/memory_service.py`)
- Provides high-level CRUD, natural intent parsing ("Remember that...", "Forget..."), implicit candidate extraction from conversation context, and hybrid retrieval.
- Enforces failure isolation so memory processing exceptions never disrupt user chat responses.

### 7. REST Router (`app/routers/memory.py`)
Endpoints for authenticated users:
- `GET /memory` (with optional `memory_type` and `search` params)
- `GET /memory/{id}`
- `POST /memory`
- `PUT /memory/{id}`
- `DELETE /memory/{id}`
- `POST /memory/explicit`
- `POST /memory/search`
- `GET /memory/stats`

### 8. Frontend Workspace (`Frontend/app/memory/page.tsx`)
- Interactive UI with category tabs, natural language "Teach AI" command input, add/edit modals, statistics cards, and source tags.

---

## Verification Summary
- **Backend Test Suite**: All 35 tests passing cleanly in `tests/test_memory.py`, `tests/test_api.py`, and `tests/test_conversation.py`.
- **Frontend Typecheck**: Passed `npm run typecheck` (`tsc --noEmit`) with 0 errors.
