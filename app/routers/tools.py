from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.models.user import User
from app.security.dependencies import get_current_user
from app.tools.tool_registry import tool_registry

router = APIRouter(
    prefix="/tools",
    tags=["Tools"]
)


@router.get("", response_model=List[Dict[str, Any]])
def list_available_tools(user: User = Depends(get_current_user)):
    """List all registered tools available to the authenticated user."""
    return tool_registry.export_llm_schemas(permissions=["*"])
