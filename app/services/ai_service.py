import json
import re
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session

from app.memory.memory_engine import MemoryEngine
from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config
from app.tools.tool_registry import tool_registry
from app.tools.tool_executor import tool_executor
from app.tools.tool_context import ToolExecutionContext
from app.agents.agent_service import agent_service
from app.database.connection import SessionLocal

memory_engine = MemoryEngine()
MAX_TOOL_CALL_ROUNDS = 5


def parse_tool_call_from_llm(llm_response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parses tool call JSON block from LLM output if present.
    Supports formats:
    1. ```json {"tool_call": {"name": "...", "arguments": {...}}} ```
    2. {"tool_call": {"name": "...", "arguments": {...}}}
    3. {"name": "...", "arguments": {...}} if marked as function call
    """
    text = llm_response_text.strip()

    # Look for code block markdown
    code_block_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            if "tool_call" in data and isinstance(data["tool_call"], dict):
                tc = data["tool_call"]
                if "name" in tc and "arguments" in tc:
                    return {"name": tc["name"], "arguments": tc["arguments"]}
            elif "name" in data and "arguments" in data and tool_registry.exists(data["name"]):
                return {"name": data["name"], "arguments": data["arguments"]}
    except Exception:
        pass

    return None


def ai_response(
    message: str,
    user=None,
    context=None,
    confirmation: Optional[Dict[str, Any]] = None,
    agent_id: Optional[str] = "atlas",
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Generates AI response by routing prompt through the designated RajOS Agent System."""
    context = context or {}
    user_id = getattr(user, "id", 1) if user else 1
    target_agent_id = (agent_id or context.get("agent_id") or "atlas").lower()

    close_db_on_exit = False
    if db is None:
        db = SessionLocal()
        close_db_on_exit = True

    try:
        conv_id = context.get("conversation_id")
        conversation_id_int = int(conv_id) if conv_id and str(conv_id).isdigit() else None
        history_payload = context.get("conversation_history") if isinstance(context, dict) else None

        agent_run_res = agent_service.run_agent(
            db=db,
            agent_id=target_agent_id,
            user_id=user_id,
            prompt=message,
            conversation_id=conversation_id_int,
            confirmation=confirmation,
            conversation_history=history_payload
        )

        return {
            "message": message,
            "agent_id": agent_run_res.get("agent_id", target_agent_id),
            "agent_name": agent_run_res.get("agent_name", target_agent_id.capitalize()),
            "response": agent_run_res.get("response", "No response generated."),
            "requires_confirmation": agent_run_res.get("requires_confirmation", False),
            "confirmation_details": agent_run_res.get("confirmation_details"),
            "tool_executions": agent_run_res.get("steps", [])
        }
    finally:
        if close_db_on_exit:
            db.close()
