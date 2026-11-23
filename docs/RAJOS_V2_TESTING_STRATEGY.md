# RajOS V2 Testing Strategy

## Overview

This document defines the testing strategy for RajOS V2, covering unit tests, integration tests, frontend tests, security tests, and CI/CD quality gates. The strategy ensures comprehensive coverage while preserving existing functionality and avoiding destructive database operations.

---

## 1. Test Architecture

### 1.1 Test Levels

| Level | Scope | Framework | Key Focus |
|-------|-------|-----------|-----------|
| **Unit Tests** | Individual functions, services, models | `pytest` | Isolation, correct output, edge cases |
| **Integration Tests** | API endpoints, database operations, real-time events | `pytest` + `TestClient` | User flows, ownership, persistence |
| **Frontend Tests** | React components, API client, state management | `jest`/`@testing-library/react` | UI interactions, event handling |
| **Security Tests** | Authz, input validation, privilege escalation | `pytest` + custom fixtures | IDOR, XSS, injection prevention |
| **Integration E2E** | Full user workflows | `pytest` with isolated DB | Complete flows from registration to notification |

### 1.2 Test Database Policy

- **Never modify the real production database** (`./rajos.db`).
- All tests use an **in-memory SQLite database** or a **temporary file DB** in the OS temp directory.
- Test database path: `os.path.join(tempfile.gettempdir(), f"rajos_test_app_{uuid.uuid4().hex[:8]}.db")`.
- Session-scoped cleanup: fixture `_cleanup_app_test_db` removes the temp DB after the test session.
- **Rollback per function**: `db_session` fixture rolls back after each test function, ensuring isolation.

### 1.3 Test Isolation Principles

- Each test gets a **fresh database session** (`db_session` fixture).
- Users are **unique per test** (suffix-based usernames/emails).
- **No shared state** between tests; rollbacks ensure cleanup.
- **External services mocked**: AI provider calls, database writes in test contexts.

---

## 2. Backend Tests

### 2.1 Authentication

| Test Name | Description |
|-----------|-------------|
| `test_register` | Validates registration with unique username/email; password hashed via bcrypt. |
| `test_login` | Validates login returns valid JWT access token. |
| `test_invalid_credentials` | Login with wrong password returns 401. |
| `test_expired_token` | Token with expired `exp` claim rejected (once `verify_exp` configured). |
| `test_unauthorized_access` | Missing/wrong token returns 401/403 on private routes. |
| `test_password_hashing` | `verify_password` correctly matches hash vs plaintext. |

### 2.2 User Isolation (Cross-User Access Prevention)

| Test Name | Description |
|-----------|-------------|
| `test_cross_user_task_access` | User A cannot see User B's tasks. |
| `test_cross_user_note_access` | User A cannot see User B's notes. |
| `test_cross_user_document_access` | User A cannot access User B's documents. |
| `test_cross_user_conversation_access` | User A cannot see User B's conversations. |
| `test_cross_user_memory_access` | User A cannot access User B's memories. |
| `test_cross_user_agent_access` | User A cannot execute User B's agents. |
| `test_cross_user_automation_access` | User A cannot run User B's automations. |
| `test_cross_user_notification_access` | User A cannot see User B's notifications. |
| `test_cross_user_search_access` | User A cannot search User B's history. |
| `test_cross_realtime_event_isolation` | SSE events for User A not delivered to User B (tested via `ConnectionManager`). |

### 2.3 AI Systems

| Test Name | Description |
|-----------|-------------|
| `test_provider_success` | Gemini provider returns valid response. |
| `test_provider_failure` | Provider error does not crash app; error event delivered. |
| `test_provider_timeout` | Timeout handled; `timeout` status in `AgentRunModel`. |
| `test_provider_fallback` | Local fallback when Gemini key missing. |
| `test_invalid_response_handling` | Malformed LLM response does not cause 500. |
| `test_streaming_behavior` | SSE stream yields `message_start → content_delta* → message_complete`. |
| `test_conversation_persistence` | Messages persisted; retrievable after restart. |

### 2.4 Memory and Knowledge

| Test Name | Description |
|-----------|-------------|
| `test_memory_retrieval` | `Memory.search` returns user-owned memories. |
| `test_memory_ownership` | Cross-user memory access blocked. |
| `test_knowledge_retrieval` | `KnowledgeService.search_knowledge` filters by `user_id`. |
| `test_document_permissions` | Document access requires ownership. |
| `test_rag_source_handling` | RAG chunks served with safe metadata only. |

### 2.5 Tool Registry and Agents

| Test Name | Description |
|-----------|-------------|
| `test_invalid_tool_arguments` | Wrong args return `INVALID_ARGUMENTS` error. |
| `test_unauthorized_tool_execution` | User without permission blocked. |
| `test_confirmation_requirements` | Confirmation-required tools need explicit approval. |
| `test_agent_execution_limits` | `max_steps` and `max_tool_caps` enforced. |
| `test_agent_cancellation` | Cancel request stops in-flight agent. |
| `test_tool_execution_failure` | Tool failure recorded; automation continues or stops per policy. |

### 2.6 Automation

| Test Name | Description |
|-----------|-------------|
| `test_schedule_validation` | Invalid trigger/conditions/actions raise `ValueError`. |
| `test_execution_ownership` | Automation only runs for owner (`user_id` filter). |
| `test_duplicate_execution_prevention` | Same `execution_key` skip; idempotent. |
| `test_failure_handling` | `failure_policy` (`stop`/`continue`) respected. |
| `test_cancellation` | `cancel()` sets status to `cancelled`; in-flight run stops. |

### 2.7 Search

| Test Name | Description |
|-----------|-------------|
| `test_search_permissions` | Cross-user search results isolated. |
| `test_result_filtering` | `types` filter narrows results correctly. |
| `test_pagination` | `page`/`limit` produce correct pagination. |
| `test_provider_failures` | Failing provider returns `error` status; others continue. |

### 2.8 Database

| Test Name | Description |
|-----------|-------------|
| `test_transactions` | `db_session` rollback leaves no residual data. |
| `test_rollbacks` | Failed operations leave DB unchanged. |
| `test_migration_checks` | `alembic upgrade` head succeeds on fresh DB. |
| `test_data_consistency` | No orphaned records after test cleanup. |

---

## 3. Frontend Tests

### 3.1 Core Functionality

| Test Category | Key Tests |
|---------------|-----------|
| **Login and Registration** | Form validation, duplicate email, password strength, token storage. |
| **Protected Routes** | Unauthenticated redirect, token expiry, route guarding. |
| **API Error Handling** | Error boundaries, user-friendly messages, no stack trace leakage. |
| **Dashboard Loading** | Page renders with user data; skeleton loading state. |

### 3.2 AI Chat

| Test Category | Key Tests |
|---------------|-----------|
| **AI Chat** | Streaming response progressive rendering; stop/cancel button terminates stream; error state on provider failure; retry logic after interruption. |
| **Streaming** | `content_delta` events arrive at ~15-char chunks; `message_complete` final event; `error` event on failure; `cancelled` on stop. |
| **Stop/Cancel** | User can halt generation; `CANCELLED` SSE event delivered; partial text preserved. |
| **Error States** | Provider error displays user-friendly message; retry option available. |

### 3.3 Tasks, Notes, Documents

| Test Category | Key Tests |
|---------------|-----------|
| **Tasks** | Create, list, update, complete, delete; ownership filter; cross-user isolation. |
| **Notes** | Create, list, update, delete; content search; ownership. |
| **Documents** | Upload (if supported), list, retrieve, delete; virus/malware scanning not applicable. |

### 3.4 Memory and Knowledge Base

| Test Category | Key Tests |
|---------------|-----------|
| **Memory** | Create/retrieve/delete memories; ownership enforced; active/archived filtering. |
| **Knowledge Base** | Search with/without semantic mode; result ranking; source attribution. |

### 3.5 Agents and Automations

| Test Category | Key Tests |
|---------------|-----------|
| **Agents** | Execute agent with tool calls; step-by-step progress; cancellation; confirmation requirements; limit reached handling. |
| **Automations** | Create with trigger/conditions/actions; manual run; schedule execution; preview; history; cancellation. |
| **Notifications** | Bell icon with unread count; notification panel with read/unread state; mark-as-read functionality; mark-all-read. |

### 3.6 Responsive and Theme

| Test Category | Key Tests |
|---------------|-----------|
| **Responsive Navigation** | Navbar collapses to hamburger on mobile; drawer menu opens. |
| **Theme Behavior** | Light/dark mode toggle persists; `prefers-color-scheme` respect. |

---

## 4. Integration Tests (End-to-End Workflows)

### 4.1 Test Workflow 1: Task Creation via AI

1. **Register** and **log in** as test user.
2. **Create a task** manually (via UI or API).
3. **Ask AI to create a task** through the approved tool system (`create_task` tool).
4. **Retrieve the conversation** and verify the task appears.
5. **Verify** the task is user-scoped (cross-user check).

### 4.2 Test Workflow 2: Memory Management

1. **Register** and **log in** as test user.
2. **Save a memory** with a key/value pair.
3. **Retrieve the memory** by key.
4. **Search memories** by query.
5. **Archive/forget** the memory; verify removal from searches.

### 4.3 Test Workflow 3: Document Management

1. **Register** and **log in** as test user.
2. **Upload a supported document** (text-based).
3. **Retrieve the document** content.
4. **Search within the document** using unified search.
5. **Verify** ownership filtering (other users cannot access).

### 4.4 Test Workflow 4: Agent Execution

1. **Register** and **log in** as test user.
2. **Create/select an agent** with defined tools.
3. **Execute the agent** with a prompt.
4. **Monitor step-by-step progress** via realtime events.
5. **Cancel the execution** mid-way; verify `cancelled` status.
6. **Verify** agent completion or timeout.

### 4.5 Test Workflow 5: Automation Creation and Execution

1. **Register** and **log in** as test user.
2. **Create an automation** with a time-based trigger and tool action.
3. **Trigger the automation** manually or wait for scheduled run.
4. **Monitor execution progress** via realtime events.
5. **Verify** completion status and notification delivery.
6. **Test cancellation** mid-execution.

### 4.6 Test Workflow 6: Notification Lifecycle

1. **Register** and **log in** as test user.
2. **Perform actions** that generate notifications (task creation, automation completion, agent finish).
3. **View the bell/panel** — verify unread count.
4. **Mark individual notifications** as read; count updates.
5. **Mark all as read**; count resets to 0.
6. **Verify** new notifications after read show as unread again.

### 4.7 Test Workflow 7: Search and Discovery

1. **Register** and **log in** as test user.
2. **Create tasks, notes, memories** with distinct content.
3. **Search by query** across resource types.
4. **Filter by type, date, sort**.
5. **Verify** cross-user isolation (other users' data not exposed).
6. **Clear search history**; verify removal.

### 4.8 Test Workflow 8: Streaming AI Response

1. **Register** and **log in** as test user.
2. **Start a new chat** (or use existing conversation).
3. **Send a message** that triggers AI streaming.
4. **Observe progressive rendering** — `content_delta` events arrive token-by-token.
5. **Test stop/cancel** — user interrupts; `CANCELLED` event; partial text preserved.
6. **Test error handling** — provider failure; `error` event with retry option.
7. **Verify** `message_complete` final event with full response text.

---

## 5. Security Testing

### 5.1 Authentication Security

| Test | Description |
|------|-------------|
| `test_brute_force_login` | Rate limiting prevents rapid repeated failures (if middleware added). |
| `test_token_exposure` | No tokens in URLs, logs, or error responses. |
| `test_password_strength` | Registration rejects weak passwords (if validation added). |

### 5.2 Authorization Security

| Test | Description |
|------|-------------|
| `test_idor_task_access` | Attempting `/tasks/{id}` with another user's ID returns 404/403. |
| `test_idor_note_access` | Same for notes. |
| `test_idor_document_access` | Same for documents. |
| `test_idor_conversation_access` | Same for conversations. |
| `test_event_isolation` | SSE events for user A not delivered to user B. |

### 5.3 Input Validation Security

| Test | Description |
|------|-------------|
| `test_sql_injection_attempts` | Various SQL injection payloads rejected/sanitized. |
| `test_xss_payloads` | XSS scripts in inputs result in escaped output, not execution. |
| `test_tool_injection` | Shell/SQL tool calls blocked by `AUTOMATION_BLOCKED_TOOLS`. |
| `test_large_payload_rejection` | Oversized API requests rejected (413 or 422). |

### 5.4 AI-Specific Security

| Test | Description |
|------|-------------|
| `test_prompt_injection` | LLM prompt injection attempts result in safe refusal, not execution. |
| `test_tool_argument_sanitization` | Dangerous keywords (`execute_sql`, `drop table`, etc.) blocked. |
| `test_untrusted_document_handling` | Retrieved document content sanitized before display. |
| `test_agent_bypass_attempts` | Agent cannot bypass backend authorization via crafted inputs. |

---

## 6. Test Commands

### 6.1 Running the Full Test Suite

```bash
# Backend only (isolated test DB)
cd /d/RajOS
python3 -m pytest tests/ -v

# Specific test categories
python3 -m pytest tests/test_search.py -v
python3 -m pytest tests/ -k "cross_user" -v
python3 -m pytest tests/ -k "auth" -v

# With coverage
python3 -m pytest tests/ --cov=app --cov-report=html
```

### 6.2 Running Frontend Tests

```bash
cd /d/RajOS/Frontend
npm test  # if Jest configured
# or
npx jest --passWithNoTests
```

### 6.3 CI/CD Test Commands

```yaml
# Example GitHub Actions job
- name: Run backend tests
  run: python3 -m pytest tests/ -v

- name: Run frontend tests
  run: cd Frontend && npm test

- name: Type check
  run: cd Frontend && npx tsc --noEmit --skipLibCheck

- name: Lint
  run: cd Frontend && npm run lint

- name: Audit dependencies
  run: cd Frontend && npm audit --audit-level=high
```

---

## 7. Known Testing Limitations

| Limitation | Workaround |
|------------|------------|
| **In-memory SQLite may differ from PostgreSQL** | Test with SQLite; document production DB requirements. |
| **AI provider calls require API keys** | Mock `llm_service.generate()` in tests; use `monkeypatch` to return controlled responses. |
| **Real-time events are process-local** | `ConnectionManager` and `EventPublisher` are in-memory; multi-worker deployments need external broker (Redis, etc.). Document this limitation. |
| **File upload/download not fully tested** | No binary file test fixtures; manual testing recommended. |
| **Browser-specific frontend tests** | Requires Jest + `@testing-library/react` + jsdom setup; CI may need display server (`xvfb`). |

---

## 8. Test Data Setup

### 8.1 Test User Fixture

Every test gets a unique user:

```python
import uuid

suffix = uuid.uuid4().hex[:8]
user = User(
    username=f"testuser_{suffix}",
    email=f"test_{suffix}@rajos.io",
    password="TestPassword123!",
    notifications_enabled=True,
)
db_session.add(user)
db_session.commit()
db_session.refresh(user)
```

### 8.2 Sample Data per Workflow

Each integration test workflow sets up only the data it needs; rollbacks ensure cleanup. No test data persists beyond the test function.

### 8.3 Mocked External Calls

- `llm_service.generate()` — monkeypatch to return `{"response": "controlled text"}`.
- `genai.Client()` — mock at provider level if Gemini tests needed without real API key.
- `tool_executor.execute()` — can mock for unit tests of tool logic.

---

## 9. CI Testing Strategy

### 9.1 Required CI Checks

| Check | Command | Failure Action |
|-------|---------|----------------|
| Python compilation | `python3 -c "import app; print('ok')"` | Fail build |
| Linting | `python3 -m ruff check app/` or `npm run lint` | Fail on errors (ignore pre-existing warnings) |
| Type checking | `cd Frontend && npx tsc --noEmit --skipLibCheck` | Fail on errors |
| Unit tests | `python3 -m pytest tests/ -v --tb=short` | Fail on failures |
| Integration tests | `python3 -m pytest tests/ -v --tb=long -k "not slow"` | Fail on failures |
| Dependency checks | `python3 -m pip check` | Warn but don't fail (minor version mismatches) |
| Security audit (backend) | Not yet implemented | Document as known gap |
| Security audit (frontend) | `npm audit --audit-level=high --fail-on-severity=high` | Fail on high/critical |
| Production build | `cd Frontend && npm run build` | Fail on build errors |

### 9.2 Recommended GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          python3 -m pip install -r requirements.txt
          cd Frontend && npm ci
      
      - name: Run backend tests
        run: python3 -m pytest tests/ -v --tb=short
      
      - name: Run frontend tests
        run: cd Frontend && npm test
      
      - name: Type check
        run: cd Frontend && npx tsc --noEmit --skipLibCheck
      
      - name: Lint
        run: cd Frontend && npm run lint
      
      - name: Audit dependencies
        run: cd Frontend && npm audit --audit-level=high
      
      - name: Build production
        run: cd Frontend && npm run build
```

---

## 10. Test Coverage Goals

| Area | Current Coverage | Target Coverage |
|------|-----------------|-----------------|
| Authentication | ~80% | 95% |
| User isolation | ~70% | 90% |
| AI/LLM systems | ~50% | 80% |
| Tool registry/agents | ~60% | 85% |
| Automation | ~65% | 85% |
| Search | ~85% | 95% |
| Database | ~75% | 90% |
| Frontend UI | ~40% | 70% |
| Real-time events | ~50% | 80% |
| Notifications | ~30% | 70% |

**Overall target**: 80%+ line coverage across backend and frontend, with critical paths (auth, isolation, AI streaming) at 90%+.