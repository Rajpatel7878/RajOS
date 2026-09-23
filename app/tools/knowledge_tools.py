from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.rag.knowledge_service import KnowledgeService

knowledge_service = KnowledgeService()


class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., description="Search query string to match against knowledge base documents", min_length=1)
    limit: Optional[int] = Field(5, description="Max chunk results to retrieve", ge=1, le=20)


class SearchKnowledgeTool(ToolDefinition):
    name = "search_knowledge"
    description = "Search the user's uploaded documents and knowledge base for relevant information."
    category = ToolCategory.KNOWLEDGE
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["knowledge.read"]
    args_model = SearchKnowledgeInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = SearchKnowledgeInput(**arguments)
        db = SessionLocal()
        try:
            results = knowledge_service.search_knowledge(
                db=db,
                user_id=context.user_id,
                query_text=args.query,
                limit=args.limit or 5
            )
            return {
                "query": args.query,
                "count": len(results),
                "results": [
                    {
                        "filename": r.get("filename"),
                        "document_id": r.get("document_id"),
                        "score": round(r.get("combined_score", 0.0), 3),
                        "snippet": r.get("chunk_text", "")[:300]
                    }
                    for r in results
                ]
            }
        finally:
            db.close()
