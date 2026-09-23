import pytest
from app.database.connection import SessionLocal, Base, engine
from app.models.user import User
from app.models.task import Task
from app.models.note import Note
from app.models.memory import Memory

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_registry import tool_registry, ToolRegistry
from app.tools.tool_executor import tool_executor, ToolExecutor
from app.tools.tool_context import ToolExecutionContext
from app.tools.tool_result import ToolErrorCode

from app.tools.task_tools import CreateTaskTool, ListTasksTool, DeleteTaskTool
from app.tools.note_tools import CreateNoteTool, ListNotesTool, DeleteNoteTool
from app.tools.memory_tools import RememberTool, SearchMemoryTool, ForgetMemoryTool
from app.tools.knowledge_tools import SearchKnowledgeTool
from app.tools.search_tools import SearchWorkspaceTool


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test users
    u1 = db.query(User).filter(User.username == "tooluser1").first()
    if not u1:
        u1 = User(id=101, username="tooluser1", email="tooluser1@rajos.io", password="pw")
        db.add(u1)
    u2 = db.query(User).filter(User.username == "tooluser2").first()
    if not u2:
        u2 = User(id=102, username="tooluser2", email="tooluser2@rajos.io", password="pw")
        db.add(u2)
    db.commit()
    db.close()


def test_tool_registry_and_schema_export():
    reg = ToolRegistry()
    assert reg.exists("create_task")
    assert reg.exists("list_tasks")
    assert reg.exists("remember")
    assert reg.exists("search_knowledge")

    schemas = reg.export_llm_schemas(permissions=["*"])
    assert len(schemas) >= 15
    tool_names = [s["name"] for s in schemas]
    assert "create_task" in tool_names
    assert "delete_task" in tool_names
    assert "remember" in tool_names


def test_task_tools_lifecycle_and_user_isolation():
    ctx_user1 = ToolExecutionContext(user_id=101, permissions=["*"])
    ctx_user2 = ToolExecutionContext(user_id=102, permissions=["*"])

    # User 1 creates task
    res1 = tool_executor.execute("create_task", {"title": "User 1 Secret Task", "priority": "high"}, ctx_user1)
    assert res1.success is True
    assert res1.data["title"] == "User 1 Secret Task"
    task1_id = res1.data["task_id"]

    # User 2 lists tasks -> should NOT see User 1 task
    res2 = tool_executor.execute("list_tasks", {}, ctx_user2)
    assert res2.success is True
    u2_task_ids = [t["id"] for t in res2.data["tasks"]]
    assert task1_id not in u2_task_ids

    # User 1 lists tasks -> sees task
    res1_list = tool_executor.execute("list_tasks", {}, ctx_user1)
    assert res1_list.success is True
    u1_task_ids = [t["id"] for t in res1_list.data["tasks"]]
    assert task1_id in u1_task_ids


def test_confirmation_policy_for_destructive_tools():
    ctx = ToolExecutionContext(user_id=101, permissions=["*"])

    # delete_task without explicit confirmation bypass -> requires confirmation
    res = tool_executor.execute("delete_task", {"task_id": 999}, ctx)
    assert res.success is False
    assert res.requires_confirmation is True
    assert res.error.code == ToolErrorCode.CONFIRMATION_REQUIRED
    assert res.confirmation_token is not None

    # delete_task WITH confirmation bypass
    res_confirmed = tool_executor.execute("delete_task", {"task_id": 999}, ctx, bypass_confirmation=True)
    assert res_confirmed.success is False  # resource not found because id 999 doesn't exist
    assert res_confirmed.error.code == ToolErrorCode.RESOURCE_NOT_FOUND


def test_invalid_argument_validation():
    ctx = ToolExecutionContext(user_id=101, permissions=["*"])

    # Invalid priority
    res = tool_executor.execute("create_task", {"title": "Bad Priority Task", "priority": "super-ultra"}, ctx)
    assert res.success is False
    assert res.error.code == ToolErrorCode.INVALID_ARGUMENTS


def test_security_blocked_payloads():
    ctx = ToolExecutionContext(user_id=101, permissions=["*"])

    # SQL Injection payload attempt
    res = tool_executor.execute("search_notes", {"query": "test; DROP TABLE tasks;--"}, ctx)
    assert res.success is False
    assert res.error.code == ToolErrorCode.INVALID_ARGUMENTS


def test_permission_denied():
    ctx_no_perm = ToolExecutionContext(user_id=101, permissions=[])

    res = tool_executor.execute("create_task", {"title": "Unauthorized Task"}, ctx_no_perm)
    assert res.success is False
    assert res.error.code == ToolErrorCode.PERMISSION_DENIED


def test_note_and_memory_tools():
    ctx = ToolExecutionContext(user_id=101, permissions=["*"])

    # Create Note
    res_note = tool_executor.execute("create_note", {"title": "DSA Study Notes", "content": "Linked lists use pointers."}, ctx)
    assert res_note.success is True
    note_id = res_note.data["note_id"]

    # Search Notes
    res_search_n = tool_executor.execute("search_notes", {"query": "pointers"}, ctx)
    assert res_search_n.success is True
    assert res_search_n.data["count"] >= 1

    # Memory Remember
    res_mem = tool_executor.execute("remember", {"key": "pref_lang", "value": "C++"}, ctx)
    assert res_mem.success is True

    # Memory Search
    res_mem_s = tool_executor.execute("search_memory", {"query": "pref_lang"}, ctx)
    assert res_mem_s.success is True
    assert res_mem_s.data["count"] >= 1
