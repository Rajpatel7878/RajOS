"""Phase 10 — Unified Search tests.

Covers resource search, ranking/filtering, history, authentication, cross-user
isolation, provider isolation, validation and schema/navigation contracts.
"""

from datetime import datetime, timedelta
import uuid

import pytest

from app.models.conversation import Conversation
from app.models.document import Document
from app.models.memory import Memory
from app.models.message import Message
from app.models.note import Note
from app.models.task import Task
from app.models.user import User
from app.search.providers.base import ProviderHit, SearchProvider
from app.search.unified_search_service import UnifiedSearchService
from app.tools.tool_context import ToolExecutionContext
from app.tools.tool_registry import tool_registry

ALLOWED_DESTINATIONS = {"/tasks", "/notes", "/documents", "/chat", "/memory"}


# ----------------------------------------------------------------------
# Fixtures and helpers
# ----------------------------------------------------------------------
@pytest.fixture
def auth_context(client, db_session):
    """A freshly registered user + bearer headers, isolated per test."""
    suffix = uuid.uuid4().hex[:8]
    email = f"search_{suffix}@rajos.io"
    password = "SearchPassword123!"

    register = client.post(
        "/register",
        json={"username": f"searchuser_{suffix}", "email": email, "password": password},
    )
    assert register.status_code in (200, 201), register.text

    login = client.post("/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text

    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    return user, {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture
def auth_headers(auth_context):
    return auth_context[1]


@pytest.fixture
def api_user(auth_context):
    """The authenticated user for this test."""
    return auth_context[0]


@pytest.fixture
def workspace(db_session, api_user):
    """A small, distinctive workspace owned by the authenticated user."""
    now = datetime.utcnow()

    task = Task(
        title="Quarterly roadmap review",
        description="Prepare the quarterly roadmap slides for the planning meeting",
        priority="high",
        category="Work",
        user_id=api_user.id,
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=2),
    )
    note = Note(
        title="Meeting notes",
        content="Discussed the quarterly roadmap and assigned owners for each workstream.",
        user_id=api_user.id,
        created_at=now - timedelta(days=4),
        updated_at=now - timedelta(days=1),
    )
    document = Document(
        title="Strategy brief",
        filename="strategy.txt",
        content="The quarterly roadmap prioritises reliability and search quality.",
        mime_type="text/plain",
        file_size=80,
        status="ready",
        user_id=api_user.id,
        created_at=now - timedelta(days=6),
        updated_at=now - timedelta(days=5),
    )
    processing_document = Document(
        title="Draft roadmap scratch",
        filename="draft.txt",
        content="quarterly roadmap draft that is still processing",
        mime_type="text/plain",
        file_size=10,
        status="processing",
        user_id=api_user.id,
        created_at=now,
        updated_at=now,
    )
    conversation = Conversation(
        title="Planning discussion",
        user_id=api_user.id,
        created_at=now - timedelta(days=8),
        updated_at=now - timedelta(days=7),
    )
    memory_active = Memory(
        key="roadmap_owner",
        value="The quarterly roadmap owner is Priya",
        memory_type="project",
        source="explicit_user",
        status="active",
        user_id=api_user.id,
        created_at=now - timedelta(days=9),
        updated_at=now - timedelta(days=9),
    )
    memory_archived = Memory(
        key="old roadmap",
        value="quarterly roadmap archived note",
        memory_type="project",
        status="archived",
        user_id=api_user.id,
        created_at=now,
        updated_at=now,
    )

    db_session.add_all(
        [task, note, document, processing_document, conversation, memory_active, memory_archived]
    )
    db_session.commit()

    message = Message(
        role="assistant",
        content="I drafted the quarterly roadmap milestones and the delivery timeline.",
        conversation_id=conversation.id,
        created_at=now - timedelta(days=7),
    )
    db_session.add(message)
    db_session.commit()

    for obj in [task, note, document, conversation, memory_active]:
        db_session.refresh(obj)

    return {
        "task": task,
        "note": note,
        "document": document,
        "processing_document": processing_document,
        "conversation": conversation,
        "memory": memory_active,
    }


def _search(client, headers, **params):
    response = client.get("/search", params=params, headers=headers)
    return response


# ----------------------------------------------------------------------
# 1-5: each supported resource type
# ----------------------------------------------------------------------
def test_search_tasks(client, auth_headers, workspace):
    response = _search(client, auth_headers, q="roadmap", types="tasks")
    assert response.status_code == 200
    payload = response.json()

    assert payload["pagination"]["total"] >= 1
    item = next(item for item in payload["items"] if item["resource_type"] == "tasks")
    assert item["resource_id"] == str(workspace["task"].id)
    assert item["url"] == "/tasks"
    assert "title" in item["matched_fields"]
    assert "roadmap" in item["title"].lower()


def test_search_notes_by_body(client, auth_headers, workspace):
    response = _search(client, auth_headers, q="workstream", types="notes")
    assert response.status_code == 200
    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["resource_type"] == "notes"
    assert items[0]["resource_id"] == str(workspace["note"].id)
    assert "content" in items[0]["matched_fields"]
    assert "workstream" in items[0]["snippet"].lower()


def test_search_documents_ready_only(client, auth_headers, workspace):
    response = _search(client, auth_headers, q="reliability", types="documents")
    items = response.json()["items"]

    document_ids = {item["resource_id"] for item in items}
    assert str(workspace["document"].id) in document_ids
    # Processing documents are not searchable.
    assert str(workspace["processing_document"].id) not in document_ids
    assert all(item["resource_type"] == "documents" for item in items)
    assert all(item["url"] == "/documents" for item in items)


def test_search_conversation_messages_grouped(client, auth_headers, workspace):
    response = _search(client, auth_headers, q="milestones", types="conversations")
    payload = response.json()
    items = payload["items"]

    assert len(items) == 1
    assert items[0]["resource_id"] == str(workspace["conversation"].id)
    assert items[0]["url"] == "/chat"
    assert "milestones" in items[0]["snippet"].lower()
    assert payload["providers"][0]["result_count"] == 1


def test_search_memories_active_only(client, auth_headers, workspace):
    response = _search(client, auth_headers, q="Priya", types="memories")
    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["resource_id"] == str(workspace["memory"].id)
    assert items[0]["title"] == "roadmap_owner"

    archived = _search(client, auth_headers, q="archived", types="memories")
    assert archived.json()["pagination"]["total"] == 0


def test_search_knowledge_semantic_provider(client, auth_headers, workspace, monkeypatch):
    calls = {}

    def fake_search_knowledge(db, user_id, query_text, limit=5):
        calls["query"] = query_text
        calls["user_id"] = user_id
        return [
            {
                "chunk_id": f"doc_{workspace['document'].id}_chunk_0",
                "document_id": workspace["document"].id,
                "filename": "strategy.txt",
                "heading": "Roadmap",
                "content": "Semantic retrieval confirms the roadmap prioritises reliability.",
                "score": 0.82,
            }
        ]

    monkeypatch.setattr(
        "app.search.providers.knowledge_provider.knowledge_service.search_knowledge",
        fake_search_knowledge,
    )

    response = _search(
        client, auth_headers, q="reliability roadmap", types="knowledge", semantic="true"
    )
    assert response.status_code == 200
    payload = response.json()

    assert calls["query"] == "reliability roadmap"
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["resource_type"] == "knowledge"
    assert item["resource_id"] == str(workspace["document"].id)
    assert item["metadata"]["chunk_id"].startswith("doc_")
    assert item["relevance_score"] > 0
    assert payload["providers"][0]["status"] == "ok"

    # Without semantic=true the knowledge provider is explicitly disabled.
    lexical = _search(client, auth_headers, q="reliability roadmap", types="knowledge")
    assert lexical.json()["items"] == []
    assert lexical.json()["providers"][0]["status"] == "disabled"


# ----------------------------------------------------------------------
# 6-11: behavior, filters, sorting, pagination, dedupe, history
# ----------------------------------------------------------------------
def test_search_no_matches_returns_empty_state(client, auth_headers):
    payload = _search(client, auth_headers, q="zzzz-no-such-thing-zzzz").json()
    assert payload["items"] == []
    assert payload["pagination"]["total"] == 0
    assert payload["pagination"]["total_pages"] == 0
    assert payload["pagination"]["has_next"] is False


def test_case_insensitive_and_partial_matching(client, auth_headers, workspace):
    upper = _search(client, auth_headers, q="QUART", types="notes")
    lower = _search(client, auth_headers, q="quart", types="notes")

    assert upper.status_code == 200
    assert upper.json()["pagination"]["total"] >= 1
    assert upper.json()["items"][0]["resource_id"] == str(workspace["note"].id)
    assert upper.json()["pagination"]["total"] == lower.json()["pagination"]["total"]


def test_resource_type_filtering_and_legacy_type_param(client, auth_headers, workspace):
    only_notes = _search(client, auth_headers, q="roadmap", types="notes").json()
    assert {item["resource_type"] for item in only_notes["items"]} == {"notes"}

    legacy = _search(client, auth_headers, q="roadmap", type="tasks").json()
    assert {item["resource_type"] for item in legacy["items"]} == {"tasks"}

    multiple = _search(client, auth_headers, q="roadmap", types="tasks,memories").json()
    assert {item["resource_type"] for item in multiple["items"]} <= {"tasks", "memories"}
    assert multiple["filters"]["resource_types"] == ["tasks", "memories"]


def test_sorting_and_pagination(client, auth_headers, db_session, api_user):
    now = datetime.utcnow()
    for index, title in enumerate(["Plan alpha", "Plan beta", "Plan gamma"]):
        db_session.add(
            Note(
                title=title,
                content=f"planning note {index}",
                user_id=api_user.id,
                created_at=now - timedelta(days=index),
                updated_at=now - timedelta(days=index),
            )
        )
    db_session.commit()

    newest = _search(
        client, auth_headers, q="plan", types="notes", sort="newest", limit=2, page=1
    ).json()
    assert newest["pagination"]["total"] == 3
    assert newest["pagination"]["total_pages"] == 2
    assert newest["pagination"]["has_next"] is True
    assert newest["pagination"]["has_previous"] is False
    assert [item["title"] for item in newest["items"]] == ["Plan alpha", "Plan beta"]

    page_two = _search(
        client, auth_headers, q="plan", types="notes", sort="newest", limit=2, page=2
    ).json()
    assert [item["title"] for item in page_two["items"]] == ["Plan gamma"]
    assert page_two["pagination"]["has_previous"] is True
    assert page_two["pagination"]["has_next"] is False

    oldest = _search(
        client, auth_headers, q="plan", types="notes", sort="oldest", limit=3
    ).json()
    assert [item["title"] for item in oldest["items"]] == ["Plan gamma", "Plan beta", "Plan alpha"]

    relevance = _search(
        client, auth_headers, q="Plan alpha", types="notes", sort="relevance", limit=3
    ).json()
    assert relevance["items"][0]["title"] == "Plan alpha"
    scores = [item["relevance_score"] for item in relevance["items"]]
    assert scores == sorted(scores, reverse=True)


def test_duplicate_results_are_removed(client, auth_headers, db_session, api_user):
    conversation = Conversation(title="budget planning", user_id=api_user.id)
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)

    for index in range(3):
        db_session.add(
            Message(
                role="user",
                content=f"budget planning detail {index}",
                conversation_id=conversation.id,
            )
        )
    db_session.commit()

    payload = _search(
        client, auth_headers, q="budget planning", types="conversations"
    ).json()
    ids = [item["id"] for item in payload["items"]]
    assert len(ids) == len(set(ids))
    assert payload["pagination"]["total"] == 1


def test_search_reflects_updates_and_deletions(client, auth_headers, db_session, api_user):
    note = Note(
        title="Consistency probe",
        content="original phrasing zetaunique",
        user_id=api_user.id,
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    found = _search(client, auth_headers, q="zetaunique", types="notes").json()
    assert found["pagination"]["total"] == 1

    note.title = "Consistency probe renamed"
    note.content = "replacement phrasing omegaunique"
    db_session.commit()

    stale = _search(client, auth_headers, q="zetaunique", types="notes").json()
    assert stale["pagination"]["total"] == 0
    fresh = _search(client, auth_headers, q="omegaunique", types="notes").json()
    assert fresh["pagination"]["total"] == 1

    db_session.delete(note)
    db_session.commit()

    removed = _search(client, auth_headers, q="omegaunique", types="notes").json()
    assert removed["pagination"]["total"] == 0


def test_legacy_trailing_slash_path_still_works(client, auth_headers):
    response = client.get("/search/?q=anything", headers=auth_headers, follow_redirects=True)
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_empty_query_returns_safe_empty_response(client, auth_headers):
    response = client.get("/search", params={"q": "   "}, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["pagination"]["total"] == 0
    assert all(status["status"] == "skipped" for status in payload["providers"])

    # Whitespace-only queries must not pollute history.
    history = client.get("/search/history", headers=auth_headers).json()["items"]
    assert history == []


def test_search_history_creation_and_retrieval(client, auth_headers):
    _search(client, auth_headers, q="history probe alpha")
    _search(client, auth_headers, q="history probe alpha")
    _search(client, auth_headers, q="history probe beta", types="notes")

    history = client.get("/search/history", headers=auth_headers)
    assert history.status_code == 200
    queries = [item["query"] for item in history.json()["items"]]
    assert queries.count("history probe alpha") == 1
    assert "history probe beta" in queries
    assert queries.index("history probe beta") < queries.index("history probe alpha")


def test_clear_search_history_is_user_scoped(client, auth_headers):
    _search(client, auth_headers, q="clear me")
    cleared = client.delete("/search/history", headers=auth_headers)
    assert cleared.status_code == 200
    assert cleared.json()["cleared"] >= 1

    remaining = client.get("/search/history", headers=auth_headers).json()["items"]
    assert remaining == []


# ----------------------------------------------------------------------
# 12-16: security, isolation, provider failures
# ----------------------------------------------------------------------
def test_search_requires_authentication(client):
    response = client.get("/search", params={"q": "roadmap"})
    assert response.status_code in (401, 403)


def test_cross_user_isolation(client, auth_headers, workspace, db_session):
    suffix = uuid.uuid4().hex[:8]
    other_email = f"other_{suffix}@rajos.io"
    client.post(
        "/register",
        json={
            "username": f"other_{suffix}",
            "email": other_email,
            "password": "OtherPassword123!",
        },
    )
    login = client.post(
        "/login", json={"email": other_email, "password": "OtherPassword123!"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    leaked = _search(client, other_headers, q="Priya", types="memories").json()
    assert leaked["items"] == []

    leaked_docs = _search(client, other_headers, q="reliability", types="documents").json()
    assert leaked_docs["items"] == []

    # Suggestions are user-scoped as well.
    suggestions = client.get(
        "/search/suggestions", params={"q": "Quarterly"}, headers=other_headers
    ).json()
    assert suggestions["suggestions"] == []

    # The owning user still sees the result.
    mine = _search(client, auth_headers, q="Priya", types="memories").json()
    assert mine["pagination"]["total"] == 1


def test_suggestions_are_bounded_and_include_history(client, auth_headers, workspace):
    _search(client, auth_headers, q="roadmap")

    response = client.get(
        "/search/suggestions", params={"q": "road", "limit": 3}, headers=auth_headers
    )
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert 1 <= len(suggestions) <= 3
    assert any(item["kind"] == "history" and "roadmap" in item["text"] for item in suggestions)
    assert all(item["text"] for item in suggestions)

    # Empty queries only expose the user's own history, never a title dump.
    empty = client.get("/search/suggestions", params={"q": ""}, headers=auth_headers).json()
    assert all(item["kind"] == "history" for item in empty["suggestions"])


def test_provider_failure_is_isolated(db_session, api_user):
    class FailingProvider(SearchProvider):
        resource_type = "tasks"
        display_name = "Tasks"

        def search(self, db, user_id, query, limit):
            raise RuntimeError("database exploded with secret details")

    class WorkingProvider(SearchProvider):
        resource_type = "notes"
        display_name = "Notes"
        default_url = "/notes"

        def search(self, db, user_id, query, limit):
            return [
                ProviderHit(
                    resource_type="notes",
                    resource_id="1",
                    title="Working note",
                    snippet="working note content",
                    url="/notes",
                    matched_fields=["title"],
                    lexical_score=0.9,
                )
            ]

    service = UnifiedSearchService(providers=[FailingProvider(), WorkingProvider()])
    response = service.search(
        db=db_session,
        user_id=api_user.id,
        query="working",
        resource_types=["tasks", "notes"],
        limit=10,
        record_history=False,
    )

    statuses = {status.resource_type: status for status in response.providers}
    assert statuses["tasks"].status == "error"
    assert "secret" not in (statuses["tasks"].error or "").lower()
    assert statuses["notes"].status == "ok"
    assert [item.title for item in response.items] == ["Working note"]


# ----------------------------------------------------------------------
# 17-20: validation, schema, navigation, tool integration
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 51},
        {"page": 0},
        {"page": 1001},
        {"types": "unicorns"},
        {"sort": "sideways"},
        {"date_from": "2026-05-01T00:00:00", "date_to": "2026-01-01T00:00:00"},
        {"q": "x" * 201},
    ],
)
def test_invalid_filters_and_limits_are_rejected(client, auth_headers, params):
    response = client.get("/search", params=params, headers=auth_headers)
    assert response.status_code == 422


def test_result_schema_and_safe_destinations(client, auth_headers, workspace):
    payload = _search(client, auth_headers, q="roadmap").json()

    assert set(payload) >= {"query", "items", "pagination", "filters", "providers", "took_ms"}
    assert payload["items"], "expected at least one result"

    for item in payload["items"]:
        assert isinstance(item["id"], str) and item["id"]
        assert isinstance(item["resource_id"], str)
        assert item["resource_type"] in {
            "tasks",
            "notes",
            "documents",
            "conversations",
            "memories",
            "knowledge",
        }
        assert item["title"]
        assert isinstance(item["matched_fields"], list)
        assert 0.0 <= item["relevance_score"] <= 1.0
        assert item["url"] in ALLOWED_DESTINATIONS

    for status in payload["providers"]:
        assert status["status"] in {"ok", "error", "disabled", "skipped"}
        assert status["duration_ms"] >= 0


def test_date_range_filter(client, auth_headers, db_session, api_user):
    old = Note(
        title="Ancient chronicle",
        content="ancient wisdom",
        user_id=api_user.id,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2020, 1, 1),
    )
    recent = Note(
        title="Modern chronicle",
        content="modern wisdom",
        user_id=api_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add_all([old, recent])
    db_session.commit()

    after_2024 = _search(
        client,
        auth_headers,
        q="chronicle",
        types="notes",
        date_from="2024-01-01T00:00:00",
    ).json()
    titles = [item["title"] for item in after_2024["items"]]
    assert "Modern chronicle" in titles
    assert "Ancient chronicle" not in titles

    before_2024 = _search(
        client,
        auth_headers,
        q="chronicle",
        types="notes",
        date_to="2024-01-01T00:00:00",
    ).json()
    titles = [item["title"] for item in before_2024["items"]]
    assert "Ancient chronicle" in titles
    assert "Modern chronicle" not in titles


def test_filters_endpoint_lists_supported_resources(client, auth_headers):
    response = client.get("/search/filters", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    values = {entry["value"] for entry in payload["resource_types"]}
    assert values == {
        "tasks",
        "notes",
        "documents",
        "conversations",
        "memories",
        "knowledge",
    }
    assert payload["max_limit"] == 50
    assert payload["max_query_length"] == 200
    assert {sort["value"] for sort in payload["sorts"]} == {"relevance", "newest", "oldest"}


def test_unified_search_tool_is_registered_and_user_scoped(api_user):
    tool = tool_registry.get_tool("unified_search")
    assert tool is not None

    context = ToolExecutionContext(user_id=api_user.id, permissions=["*"])
    create_tool = tool_registry.get_tool("create_task")
    created = create_tool.execute(
        {"title": "Tool scoped task", "description": "tool searchable"}, context
    )
    assert created["task_id"]

    result = tool.execute({"query": "tool scoped", "resource_types": ["tasks"]}, context)
    assert result["total"] >= 1
    assert result["results"][0]["type"] == "tasks"
    assert result["results"][0]["url"] == "/tasks"

    # A different user must not see the tool result.
    other_context = ToolExecutionContext(user_id=api_user.id + 100000, permissions=["*"])
    other_result = tool.execute(
        {"query": "tool scoped", "resource_types": ["tasks"]}, other_context
    )
    assert other_result["total"] == 0
