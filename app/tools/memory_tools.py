from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.memory.memory_service import MemoryService

memory_service = MemoryService()


class RememberInput(BaseModel):
    key: str = Field(..., description="Short identifier or topic of the memory (e.g. 'coding_preference', 'favorite_color')", min_length=1, max_length=100)
    value: str = Field(..., description="The factual information or preference to remember", min_length=1)
    memory_type: Optional[str] = Field("preference", description="Memory type: preference, fact, goal, detail")


class SearchMemoryInput(BaseModel):
    query: str = Field(..., description="Search query string", min_length=1)
    limit: Optional[int] = Field(10, description="Max memories to return", ge=1, le=50)


class ForgetMemoryInput(BaseModel):
    memory_id: int = Field(..., description="ID of the memory to delete/forget", ge=1)


class RememberTool(ToolDefinition):
    name = "remember"
    description = "Store a long-term memory, preference, or fact for the authenticated user."
    category = ToolCategory.MEMORY
    read_only = False
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["memory.write"]
    args_model = RememberInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = RememberInput(**arguments)
        db = SessionLocal()
        try:
            res = memory_service.create_memory(
                db=db,
                user_id=context.user_id,
                key=args.key,
                value=args.value,
                memory_type=args.memory_type or "preference",
                source="ai_tool"
            )
            mem = res.get("memory")
            return {
                "status": res.get("status"),
                "reason": res.get("reason"),
                "memory_id": mem.id if mem else None,
                "key": mem.key if mem else args.key,
                "value": mem.value if mem else args.value
            }
        finally:
            db.close()


class SearchMemoryTool(ToolDefinition):
    name = "search_memory"
    description = "Search long-term memories for relevant facts or preferences of the user."
    category = ToolCategory.MEMORY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["memory.read"]
    args_model = SearchMemoryInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = SearchMemoryInput(**arguments)
        db = SessionLocal()
        try:
            memories = memory_service.get_memories(
                db=db,
                user_id=context.user_id,
                search_query=args.query,
                status="active"
            )
            return {
                "query": args.query,
                "count": len(memories[:args.limit]),
                "memories": [
                    {
                        "id": m.id,
                        "key": m.key,
                        "value": m.value,
                        "type": m.memory_type,
                        "confidence": m.confidence
                    }
                    for m in memories[:args.limit]
                ]
            }
        finally:
            db.close()


class ForgetMemoryTool(ToolDefinition):
    name = "forget_memory"
    description = "Delete/forget a long-term memory item by ID. Requires user confirmation."
    category = ToolCategory.MEMORY
    read_only = False
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    required_permissions = ["memory.write"]
    args_model = ForgetMemoryInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = ForgetMemoryInput(**arguments)
        db = SessionLocal()
        try:
            success = memory_service.delete_memory(
                db=db,
                user_id=context.user_id,
                memory_id=args.memory_id
            )
            if not success:
                raise ValueError(f"Memory with ID {args.memory_id} was not found.")
            return {
                "memory_id": args.memory_id,
                "status": "deleted"
            }
        finally:
            db.close()
