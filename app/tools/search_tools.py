from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal

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
