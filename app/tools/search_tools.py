from typing import Any, Dict, Optional, List, Literal
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.search.unified_search_service import unified_search_service

from app.models.task import Task
from app.models.note import Note
from app.models.memory import Memory
from app.models.document import Document


class SearchWorkspaceInput(BaseModel):
    query: str = Field(..., description="Query to search across user's workspace (tasks, notes, memory, documents)", min_length=1)
    limit: Optional[int] = Field(10, description="Max total results per entity type", ge=1, le=50)


class SearchWorkspaceTool(ToolDefinition):
    name = "search_workspace"
    description = "Search across all user workspace items including tasks, notes, memory, and documents."
    category = ToolCategory.SEARCH
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["search.read"]
    args_model = SearchWorkspaceInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = SearchWorkspaceInput(**arguments)
        db = SessionLocal()
        pattern = f"%{args.query}%"
        limit = args.limit or 10

        try:
            tasks = db.query(Task).filter(
                Task.user_id == context.user_id,
                (Task.title.ilike(pattern)) | (Task.description.ilike(pattern))
            ).limit(limit).all()

            notes = db.query(Note).filter(
                Note.user_id == context.user_id,
                (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
            ).limit(limit).all()

            memories = db.query(Memory).filter(
                Memory.user_id == context.user_id,
                Memory.status == "active",
                (Memory.key.ilike(pattern)) | (Memory.value.ilike(pattern)) | (Memory.content.ilike(pattern))
            ).limit(limit).all()

            documents = db.query(Document).filter(
                Document.user_id == context.user_id,
                (Document.title.ilike(pattern)) | (Document.filename.ilike(pattern))
            ).limit(limit).all()

            return {
                "query": args.query,
                "tasks": [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks],
                "notes": [{"id": n.id, "title": n.title, "snippet": n.content[:100] if n.content else ""} for n in notes],
                "memories": [{"id": m.id, "key": m.key, "value": m.value} for m in memories],
                "documents": [{"id": d.id, "title": d.title, "filename": d.filename} for d in documents]
            }
        finally:
            db.close()


class UnifiedSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Workspace search query (tasks, notes, documents, conversations, memories, knowledge)",
        min_length=1,
        max_length=200,
    )
    resource_types: Optional[List[Literal[
        "tasks", "notes", "documents", "conversations", "memories", "knowledge"
    ]]] = Field(
        None,
        description="Optional resource types to search; omit to search all supported types",
    )
    limit: Optional[int] = Field(10, description="Maximum results to return", ge=1, le=25)
    include_semantic: Optional[bool] = Field(
        False,
        description="Include semantic knowledge-base retrieval (slower, embedding-based)",
    )


class UnifiedSearchTool(ToolDefinition):
    """Expose the unified workspace search to AI agents and chat."""

    name = "unified_search"
    description = (
        "Search the authenticated user's entire RajOS workspace: tasks, notes, documents, "
        "conversations, memories and (optionally) semantic knowledge-base passages. "
        "Returns ranked results with resource type, id, snippet and workspace URL."
    )
    category = ToolCategory.SEARCH
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["search.read"]
    args_model = UnifiedSearchInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = UnifiedSearchInput(**arguments)
        db = SessionLocal()
        try:
            response = unified_search_service.search(
                db=db,
                user_id=context.user_id,
                query=args.query,
                resource_types=args.resource_types,
                limit=args.limit or 10,
                semantic=bool(args.include_semantic),
                # Tool calls must not pollute the user's visible search history.
                record_history=False,
            )
            return {
                "query": response.query,
                "total": response.pagination.total,
                "results": [
                    {
                        "id": item.id,
                        "type": item.resource_type,
                        "title": item.title,
                        "snippet": item.snippet[:300],
                        "url": item.url,
                        "score": item.relevance_score,
                        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                    }
                    for item in response.items
                ],
                "providers": [
                    {
                        "resource_type": status.resource_type,
                        "status": status.status,
                    }
                    for status in response.providers
                ],
            }
        finally:
            db.close()
