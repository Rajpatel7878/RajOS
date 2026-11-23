# RajOS V2 — Phase 10: Search & Unified Workspace

Status: implemented.

Phase 10 connects RajOS's existing resources into one authenticated, ranked
search surface. It **extends** the existing `app/search/` package, the existing
RAG/vector pipeline, and the existing Tool Registry. It does not introduce a
second search index, a second vector database, or an external search service.

---

## 1. Architecture

```text
User (Next.js /search workspace)
      │  Bearer JWT
      ▼
GET /search  (FastAPI, authenticated)
      │
      ▼
UnifiedSearchService
      │  1. normalize + sanitize query (bounded, word-character terms)
      │  2. validate resource types, dates, sort, page, limit
      │  3. resolve providers (selected types only)
      │
      ├── TaskSearchProvider          ── tasks table
      ├── NoteSearchProvider          ── notes table
      ├── DocumentSearchProvider      ── documents table (status = ready)
      ├── ConversationSearchProvider  ── conversations + messages
      ├── MemorySearchProvider        ── memories table (status = active)
      └── KnowledgeSearchProvider     ── existing hybrid RAG retriever (opt-in)
      │
      │  4. per-provider try/except + timing (failures are isolated)
      ▼
Ranking & deduplication
      │  deterministic lexical score, optional semantic blend, 3 % recency
      │  dedupe by (resource type, resource id / chunk id)
      ▼
Filters → sorting → pagination → UnifiedSearchResponse
      │
      ├── search history (user-scoped, frontend recent searches)
      └── AI: unified_search tool (Tool Registry → agents/chat)
```

Key modules:

| File | Responsibility |
| --- | --- |
| `app/search/search_router.py` | Authenticated HTTP endpoints |
| `app/search/unified_search_service.py` | Orchestration, ranking, dedupe, suggestions, history |
| `app/search/search_models.py` | Pydantic request/response schemas |
| `app/search/providers/base.py` | `SearchProvider`, `ProviderQuery`, `ProviderHit` |
| `app/search/providers/*.py` | One provider per resource type |
| `app/search/utils/scoring.py` | Pure deterministic scoring/snippet utilities |
| `app/search/history_service.py` | User-scoped search history |
| `app/tools/search_tools.py` | `unified_search` tool for AI agents |
| `Frontend/app/search/page.tsx` | Unified Workspace UI |
| `Frontend/services/api/search.ts` | Typed frontend API client |

The legacy `SearchService` import path is preserved as a thin subclass of
`UnifiedSearchService`, so there is only one search implementation.

---

## 2. Supported resource types

| Type | Source | Searchable fields | Destination |
| --- | --- | --- | --- |
| `tasks` | `tasks` | title, description, category, tags | `/tasks` |
| `notes` | `notes` | title, content | `/notes` |
| `documents` | `documents` (`status = ready`) | title, filename, content | `/documents` |
| `conversations` | `conversations` + `messages` | conversation title, message content | `/chat` |
| `memories` | `memories` (`status = active`) | key, value, content | `/memory` |
| `knowledge` | existing RAG chunk index + `documents` | semantic + lexical chunk text, document title | `/documents` |

`knowledge` is opt-in (`semantic=true`) because it uses embeddings through the
existing RAG pipeline. All other providers are ordinary, deterministic database
queries.

Only destinations that exist in the current frontend are emitted. A resource
without a supported page is returned with `url: null` and rendered as
non-clickable rather than linking to a broken route.

---

## 3. Search provider interface

```python
class SearchProvider(ABC):
    resource_type: str
    display_name: str
    default_url: str | None

    def available(self) -> bool: ...
    def unavailable_reason(self) -> str | None: ...
    def skip_reason(self, query: ProviderQuery) -> str | None: ...

    @abstractmethod
    def search(
        self, db: Session, user_id: int, query: ProviderQuery, limit: int
    ) -> list[ProviderHit]: ...

    def suggest(
        self, db: Session, user_id: int, query: str,
        terms: Sequence[str], limit: int
    ) -> list[dict]: ...
```

Each provider:

- receives an already-authenticated `user_id` from the service (never from the
  client),
- filters `user_id` in every SQL query,
- applies date-range filters on `updated_at` (messages use `created_at`),
- returns at most `limit` candidate hits, and
- never raises for an empty/blank query because the service short-circuits it.

`ProviderHit` carries resource id/type, title, snippet, URL, matched fields,
timestamps, lexical/semantic scores and safe metadata. `make_hit()` applies
consistent snippet generation and field matching.

Provider failures are caught per provider in `UnifiedSearchService.search`.
The response still returns other providers' results and reports the failed
provider with `status: "error"`. The exception itself is logged server-side and
never returned to the client.

---

## 4. API endpoints

All endpoints require `Authorization: Bearer <JWT>`.

### `GET /search`

Unified workspace search.

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `q` | string | `""` | Max 200 characters; blank returns an empty, valid response |
| `types` | CSV string | all | `tasks,notes,documents,conversations,memories,knowledge` |
| `type` | string | `all` | Legacy single-type parameter (kept for compatibility) |
| `sort` | `relevance` \| `newest` \| `oldest` | `relevance` | |
| `date_from` | ISO datetime | – | Inclusive `updated_at >=` filter |
| `date_to` | ISO datetime | – | Inclusive `updated_at <=` filter |
| `page` | int | `1` | 1–1000 |
| `limit` | int | `20` | 1–50 |
| `semantic` | bool | `false` | Enables the knowledge provider |

Examples:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/search?q=roadmap&types=tasks,notes&sort=relevance&limit=10"

curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/search?q=reliability&types=knowledge&semantic=true"
```

`GET /search/` is also registered (hidden from the schema) so the legacy
trailing-slash URL keeps working.

### `GET /search/suggestions`

`q` (max 200), `limit` (1–10, default 8). Returns the user's matching recent
searches plus bounded title suggestions from tasks, notes, ready documents,
conversations and active memories. Empty `q` returns **only** the user's own
recent searches — never a dump of resource titles.

### `GET /search/history`

`limit` (1–50, default 10). Newest first, de-duplicated by query text.

### `DELETE /search/history`

Deletes only the authenticated user's history. Returns `{"cleared": n}`.

### `GET /search/filters`

Returns supported resource types (with availability), sort options,
`semantic_available`, `max_limit` and `max_query_length`.

### Example response

```json
{
  "query": "roadmap",
  "items": [
    {
      "id": "tasks:12",
      "resource_id": "12",
      "resource_type": "tasks",
      "title": "Quarterly roadmap review",
      "snippet": "Prepare the quarterly roadmap slides…",
      "url": "/tasks",
      "matched_fields": ["title", "description"],
      "created_at": "2026-10-26T10:00:00",
      "updated_at": "2026-10-27T10:00:00",
      "relevance_score": 0.9123,
      "metadata": {"completed": false, "priority": "high", "category": "Work"}
    }
  ],
  "pagination": {
    "page": 1, "limit": 20, "total": 1, "total_pages": 1,
    "has_next": false, "has_previous": false
  },
  "filters": {
    "resource_types": ["tasks", "notes", "documents", "conversations", "memories", "knowledge"],
    "date_from": null, "date_to": null, "sort": "relevance", "semantic": false
  },
  "providers": [
    {"resource_type": "tasks", "display_name": "Tasks", "status": "ok",
     "result_count": 1, "duration_ms": 2.4, "error": null},
    {"resource_type": "knowledge", "display_name": "Knowledge base",
     "status": "disabled", "result_count": 0, "duration_ms": 0.0,
     "error": "Semantic retrieval was not requested for this query."}
  ],
  "took_ms": 7.8
}
```

Validation errors return `422` with a safe message. Internal exceptions are
never serialized; provider failures are summarized.

**Compatibility note:** the pre-Phase-10 `GET /search` returned separate
`tasks`/`notes`/`memories`/`conversations`/`documents` arrays without
authentication. It is now the unified schema above and requires authentication.
No current frontend page consumed the old shape.

---

## 5. Result schema

`SearchItem` fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable result id, e.g. `tasks:12` or `knowledge:doc_4_chunk_1` |
| `resource_id` | Existing model identifier (string form) |
| `resource_type` | One of the six supported types |
| `title` | Human-readable resource title |
| `snippet` | Sanitized, query-centred excerpt (plain text) |
| `url` | Safe existing frontend destination, or `null` |
| `matched_fields` | `title`, `content`, `description`, `message`, `semantic`, … |
| `created_at` / `updated_at` | Resource timestamps when available |
| `relevance_score` | Deterministic score in `[0, 1]` (not a confidence value) |
| `metadata` | Non-sensitive source metadata (filename, priority, heading, …) |

`ProviderStatus` makes partial failures visible: `ok`, `error`, `disabled`
(e.g. semantic off / RAG disabled) or `skipped` (empty query or time budget).

---

## 6. Ranking strategy

Scores are deterministic and inspectable; they are **relevance**, not
confidence.

Per hit (see `app/search/utils/scoring.py`):

```text
title_match   = exact 1.0 | prefix 0.94 | phrase 0.88
                | all terms 0.74 | partial terms ≤ 0.68 | fuzzy ≤ 0.30
body_match    = same rules over the body fields
coverage      = matched query terms / total terms

lexical = 0.60 × title_match + 0.30 × body_match + 0.10 × coverage
```

Then:

```text
text_score = lexical                                   (lexical providers)
           = 0.75 × lexical + 0.25 × semantic          (semantic hits)

recency    = 0.5 ^ (age_days / 180)                    (0..1)

score      = 0.97 × text_score + 0.03 × recency
```

Consequences:

- An exact/strong title match always outranks a merely recent body match.
- Recency can move a result by at most 3 % and never overrides text relevance.
- Semantic scores are normalized to `[0, 1]` before blending, and only used
  when a provider actually supplies one.
- Sorting modes: `relevance` (score, then newest), `newest`/`oldest`
  (`updated_at`, falling back to `created_at`), with deterministic tie-breaks.
- Duplicate `(resource_type, resource_id)` hits keep the highest score. RAG
  chunks are keyed by chunk id because they are distinct passages.
- Results with neither lexical nor semantic match are discarded; nothing is
  invented.

---

## 7. Keyword vs semantic search

- Default workspace search is **lexical and deterministic**. It makes no LLM
  and no embedding call, so ordinary queries stay fast and predictable.
- `semantic=true` additionally runs `KnowledgeSearchProvider`, which reuses
  `knowledge_service.search_knowledge()` — the existing hybrid vector + keyword
  RAG retriever. No second embedding model or vector store is created.
- Semantic knowledge results preserve `document_id`, `filename`, `heading` and
  `chunk_id`, and are re-validated against the `documents` table for ownership
  and `ready` status before being returned.
- Ordinary workspace search stays separate from knowledge-grounded answer
  generation. RAG answer context continues to be built by `ContextBuilder` /
  `KnowledgeService.build_knowledge_context`, which keeps its
  `<UNTRUSTED_KNOWLEDGE_DOCUMENT>` prompt-injection defense.
- Pre-Phase-10 semantic providers (memory and document endpoints) remain
  available at their existing dedicated routes.

---

## 8. Authentication and permissions

- `get_current_user` validates the JWT; `user.id` is the only identity used by
  the service. Client-supplied user ids are never accepted.
- Every provider query includes `user_id == authenticated_user.id`.
- Knowledge hits are cross-checked against owned, ready documents even though
  the RAG retriever already filters by user.
- Suggestions, history reads and history deletion are user-scoped.
- Search history rows created by AI tool calls are not recorded
  (`record_history=False`).
- Query text is reduced to word-character terms before it reaches SQL;
  SQLAlchemy binds all values, so there is no string-built SQL.
- Snippets strip HTML tags and control characters, collapse whitespace and are
  truncated. The UI renders them as text (no `dangerouslySetInnerHTML`).
- Internal paths, prompts, API keys and raw exceptions are never included in
  results or errors.
- Indexed content is treated as data, never as instructions.

---

## 9. Indexing and consistency

Phase 10 intentionally adds **no new index store**:

- Tasks, notes, documents, conversations, memories are searched live from the
  database, so creates, updates and deletes are reflected immediately. Nothing
  can go stale after a restart.
- Processing/failed documents are excluded; archived/deleted memories are
  excluded; archived conversations remain searchable (they are still owned by
  the user and the UI marks them).
- Knowledge chunk indexing/update/deletion continues to be handled by
  `KnowledgeService` on document ingest, update and delete. Unified search only
  reads that index.
- Additive indexes are created by `app/database/schema_sync.py` (no data
  rewrites, no table drops):
  `search_history(user_id, searched_at)`, `tasks(user_id)`, `notes(user_id)`,
  `documents(user_id, status)`, `conversations(user_id)`,
  `memories(user_id, status)`, `messages(conversation_id)`.
- `search_history` gained nullable/additive `resource_types` and `result_count`
  columns through the same additive sync.

Indexing for documents remains synchronous with ingestion (existing behavior).
Unified search never triggers re-indexing.

---

## 10. Configuration

No new environment variables or dependencies are required.

| Setting | Where | Effect |
| --- | --- | --- |
| `RAG_ENABLED` | `app/rag/rag_config.py` | Disables the knowledge provider when false |
| `RAG_CANDIDATE_LIMIT` | same | Caps semantic candidates (≤ 20 in search) |
| `RAG_RELEVANCE_THRESHOLD` | same | Applied by the existing hybrid retriever |
| `MAX_QUERY_LENGTH` | `app/search/utils/scoring.py` | 200 characters |
| `MAX_LIMIT` / `MAX_PAGE` | `unified_search_service.py` | 50 results / page 1000 |
| `PROVIDER_SOFT_BUDGET_SECONDS` | same | 4 s soft budget; remaining providers are skipped |

The soft budget is checked between providers. Python cannot safely interrupt a
blocking synchronous DB call, so it bounds work rather than promising a hard
per-provider timeout.

Performance protections: bounded query length, bounded candidate limits,
parameterized queries with user indexes, no N+1 lookups (knowledge timestamps
are fetched in one query), file-type-specific limits, and semantic retrieval
only when requested. No private result caching is implemented, so cross-user
leakage through a cache is impossible.

---

## 11. Adding another search provider

1. Create `app/search/providers/<name>_provider.py`:

   ```python
   class ProjectSearchProvider(SearchProvider):
       resource_type = "projects"
       display_name = "Projects"
       default_url = "/projects"   # only if that page exists

       def search(self, db, user_id, query, limit):
           rows = (
               db.query(Project)
               .filter(Project.user_id == user_id, contains_any([Project.name], query.terms))
               .limit(limit)
               .all()
           )
           return [
               self.make_hit(
                   resource_id=row.id,
                   title=row.name,
                   snippet_source=row.description,
                   query=query,
                   fields={"title": row.name, "description": row.description},
                   created_at=row.created_at,
                   updated_at=row.updated_at,
               )
               for row in rows
           ]
   ```

2. Register the class in `DEFAULT_PROVIDER_CLASSES` in
   `app/search/providers/__init__.py`.
3. Add its value to `ResourceType` / `RESOURCE_TYPE_VALUES` in
   `app/search/search_models.py`.
4. Add the UI metadata entry (`label`, icon, colours) in
   `Frontend/app/search/page.tsx` and the safe destination in the frontend if
   a real page exists.
5. Add a test in `tests/test_search.py` covering matches, filtering and
   cross-user isolation.

Provider rules: always filter by `user_id`, never build raw SQL, keep results
bounded, return `ProviderHit` via `make_hit`, and raise on real failures (the
service isolates them).

---

## 12. AI and knowledge integration

- `unified_search` is registered in the existing `ToolRegistry`
  (`required_permissions=["search.read"]`). It calls the same service with the
  tool context's authenticated `user_id`, returns bounded structured results
  (≤ 25) and does not write search history.
- Built-in agents Atlas, Nova and Pulse are granted `unified_search`; the
  registry's additive seed updates existing built-in agent allowlists without
  removing any tools.
- The dedicated RAG pipeline (`search_knowledge`, `ContextBuilder`,
  `build_knowledge_context`) is unchanged and remains responsible for grounded
  answer generation and citations. Unified search does not replace it.
- The frontend chat does not automatically inject search results into prompts;
  agents can request `unified_search` explicitly through normal tool calling.

---

## 13. Frontend

Route `/search` (Unified Workspace):

- prominent autofocused search input, form submit, clear button;
- debounced (250 ms) suggestions with abort + duplicate-query suppression,
  arrow-key navigation, Enter to select, Escape to close;
- recent searches with clear-history, resource-type chips, sort/date/semantic
  controls, page size 20 with previous/next pagination;
- loading skeletons, empty state, error state with retry, result count and
  per-provider counts/warnings;
- results show type icon/label, title, snippet, matched fields, timestamps and
  safe metadata; valid results link to `/tasks`, `/notes`, `/documents`,
  `/chat`, `/memory`;
- responsive two-column empty state, single-column results, accessible labels,
  `aria-pressed`, `aria-expanded`, `aria-activedescendant`, focus rings;
- integrated into the existing sidebar ("Workspace → Search") and the topbar
  search control.

`Ctrl/Cmd+K` was already bound to Quick Capture, so Phase 10 does **not**
re-bind it. Search is reachable from navigation, the topbar and direct URL.

---

## 14. Tests

```bash
python -m pytest tests/test_search.py -q
python -m pytest tests -q
```

Run the suite from the `tests` directory (or target `tests`) rather than bare
`pytest`: the repository already contains two unrelated `test_security.py`
files at the root and under `backend/`, which makes bare root collection
ambiguous.

`tests/test_search.py` covers: tasks, notes, documents (ready-only),
conversations/messages, memories (active-only), knowledge provider,
no-match/empty state, case-insensitive partial matching, type filters,
sorting/pagination, duplicate removal, history create/retrieve/clear,
authentication, cross-user isolation, suggestions scoping, provider failure
isolation, malformed filters/limits, response schema, safe destinations, date
ranges, filter-options, and the `unified_search` tool.

Frontend verification uses `npx tsc --noEmit` and `npm run build`. The project
has no frontend unit-test runner configured, so UI loading/empty/error and
navigation states are verified through the type-checked implementation, the
production build and backend contract tests (including destination URLs).

---

## 15. Known limitations

- The legacy `/search` response shape changed (see compatibility note above).
- There is no full-text index (SQLite `LIKE` + deterministic scoring at bounded
  candidate sizes). This is adequate for a personal workspace; a dedicated FTS
  index would be the next step for very large datasets.
- The provider budget is soft (checked between providers, not a hard kill).
- Date filters apply to `updated_at` (messages use `created_at`); semantic
  knowledge chunks use their parent document's `updated_at`.
- Knowledge chunk text is truncated in result snippets; use `/documents` or
  RAG for full context.
- Search history is textual only (no per-result click tracking).
- Suggestions are title-based and capped; they do not semantically expand the
  query, by design.
- No private-result caching (deliberate, to keep user isolation simple).
- Frontend automated state/navigation tests are not present because the
  repository has no frontend test framework; adding one is deferred.

---

## 16. Integration points for Phase 11+

- `UnifiedSearchService.search()` is the single backend entry point for any
  future command palette, dashboard widget or realtime search.
- `Frontend/services/api/search.ts` exposes typed functions for reuse.
- `unified_search` can be offered to additional agents via their
  `allowed_tools`.
- New resource providers plug in without touching the router or ranking layer.
