import json
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session

from app.models.agent import AgentDefinitionModel, AgentRunModel
from app.agents.agent_registry import agent_registry
from app.agents.agent_context_builder import agent_context_builder
from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config
from app.tools.tool_executor import tool_executor
from app.tools.tool_context import ToolExecutionContext
from app.tools.tool_registry import tool_registry


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


class AgentService:

    def run_agent(
        self,
        db: Session,
        agent_id: str,
        user_id: int,
        prompt: str,
        conversation_id: Optional[int] = None,
        confirmation: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Orchestrates agent execution loop with step capping, capability checking, and confirmation handling."""

        # 1. Resolve agent
        agent = agent_registry.get_agent(db, agent_id, user_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' was not found.")

        if not agent.enabled:
            return {
                "run_id": "",
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": "failed",
                "error": f"Agent '{agent.name}' is currently disabled.",
                "response": f"Agent '{agent.name}' is disabled and cannot execute."
            }

        # 2. Setup Tool Execution Context
        exec_context = ToolExecutionContext(
            user_id=user_id,
            conversation_id=str(conversation_id) if conversation_id else None,
            permissions=["*"]
        )

        # 3. Handle explicit user confirmation response
        if confirmation and isinstance(confirmation, dict):
            tool_name = confirmation.get("tool_name")
            arguments = confirmation.get("arguments", {})
            confirmed = confirmation.get("confirmed", False)

            if confirmed and tool_name:
                res = tool_executor.execute(
                    tool_name=tool_name,
                    arguments=arguments,
                    context=exec_context,
                    bypass_confirmation=True
                )
                summary_prompt = f"""
Agent {agent.name}: The user confirmed execution of tool '{tool_name}'.
Tool Result:
<UNTRUSTED_TOOL_RESULT tool="{tool_name}">
{json.dumps(res.to_dict(), default=str)}
</UNTRUSTED_TOOL_RESULT>
Synthesize a clear, concise confirmation summary.
"""
                provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")
                llm_out = llm_service.generate(prompt=summary_prompt, provider=provider)
                return {
                    "run_id": confirmation.get("run_id", f"run_{uuid.uuid4().hex[:10]}"),
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "completed",
                    "response": llm_out.get("response", "Action completed."),
                    "steps": [{"step": 1, "tool_name": tool_name, "arguments": arguments, "result": res.to_dict()}]
                }
            else:
                return {
                    "run_id": f"run_{uuid.uuid4().hex[:10]}",
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "cancelled",
                    "response": f"Action '{tool_name}' was cancelled by the user.",
                    "steps": []
                }

        # 4. Create AgentRun database record
        from app.models.user import User
        db_user_id = user_id if user_id and db.query(User.id).filter(User.id == user_id).first() else None

        run_id = f"run_{uuid.uuid4().hex[:10]}"
        run_record = AgentRunModel(
            id=run_id,
            user_id=db_user_id,
            agent_id=agent.id,
            conversation_id=conversation_id,
            prompt=prompt,
            status="running",
            current_step=0,
            step_history=[],
            started_at=datetime.utcnow()
        )
        db.add(run_record)
        db.commit()

        start_time = time.time()
        step_history: List[Dict[str, Any]] = []
        recent_tool_calls: List[str] = []

        max_steps = agent.max_steps or 5
        max_tool_calls = agent.max_tool_calls or 5
        timeout_seconds = agent.timeout_seconds or 30.0

        provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

        for current_step in range(1, max_steps + 1):
            # Timeout Check
            if (time.time() - start_time) > timeout_seconds:
                run_record.status = "timeout"
                run_record.error_message = "Execution timed out."
                run_record.completed_at = datetime.utcnow()
                db.commit()
                return {
                    "run_id": run_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "timeout",
                    "response": "Agent execution timed out.",
                    "steps": step_history,
                    "error": "Timeout exceeded"
                }

            run_record.current_step = current_step
            db.commit()

            # Build Agent Context
            llm_prompt = agent_context_builder.build_prompt(
                db=db,
                agent=agent,
                user_id=user_id,
                user_prompt=prompt,
                conversation_history=conversation_history,
                step_history=step_history
            )

            # Call AI Core
            llm_out = llm_service.generate(prompt=llm_prompt, provider=provider)
            response_text = llm_out.get("response", "")

            # Interpret Agent Decision (Final Response vs Tool Call)
            tool_call = parse_tool_call_from_llm(response_text)

            if not tool_call:
                # Final response generated
                run_record.status = "completed"
                run_record.final_response = response_text
                run_record.completed_at = datetime.utcnow()
                run_record.step_history = step_history
                db.commit()

                return {
                    "run_id": run_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "completed",
                    "response": response_text,
                    "steps": step_history
                }

            # Tool Execution Path
            t_name = tool_call["name"]
            t_args = tool_call.get("arguments", {})

            # Capability & Restriction Check: Agent must have tool in allowed_tools
            if t_name not in agent.allowed_tools:
                err_msg = f"Agent '{agent.name}' is not authorized to call tool '{t_name}'."
                step_history.append({
                    "step": current_step,
                    "tool_name": t_name,
                    "arguments": t_args,
                    "result": {"success": False, "error": {"code": "PERMISSION_DENIED", "message": err_msg}}
                })
                continue

            # Protection against repeated identical tool calls
            call_key = f"{t_name}:{json.dumps(t_args, sort_keys=True)}"
            if recent_tool_calls.count(call_key) >= 2:
                run_record.status = "limit_reached"
                run_record.error_message = f"Infinite tool call loop detected for tool '{t_name}'."
                run_record.completed_at = datetime.utcnow()
                run_record.step_history = step_history
                db.commit()
                return {
                    "run_id": run_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "limit_reached",
                    "response": f"Agent stopped safely after detecting repeated tool execution ({t_name}).",
                    "steps": step_history
                }
            recent_tool_calls.append(call_key)

            # Max Tool Calls Check
            if len([s for s in step_history if "tool_name" in s]) >= max_tool_calls:
                run_record.status = "limit_reached"
                run_record.completed_at = datetime.utcnow()
                run_record.step_history = step_history
                db.commit()
                return {
                    "run_id": run_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "limit_reached",
                    "response": "Agent reached maximum allowed tool executions.",
                    "steps": step_history
                }

            # Execute Tool via ToolExecutor
            tool_res = tool_executor.execute(
                tool_name=t_name,
                arguments=t_args,
                context=exec_context
            )

            step_history.append({
                "step": current_step,
                "tool_name": t_name,
                "arguments": t_args,
                "result": tool_res.to_dict()
            })

            # Handle Confirmation Requirement
            if tool_res.requires_confirmation:
                run_record.status = "waiting_for_confirmation"
                run_record.confirmation_token = tool_res.confirmation_token
                run_record.step_history = step_history
                db.commit()

                return {
                    "run_id": run_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": "waiting_for_confirmation",
                    "response": f"Confirmation required before agent '{agent.name}' executes '{t_name}'.",
                    "requires_confirmation": True,
                    "confirmation_details": {
                        "run_id": run_id,
                        "tool_name": t_name,
                        "arguments": t_args,
                        "confirmation_token": tool_res.confirmation_token
                    },
                    "steps": step_history
                }

        # Max steps reached
        run_record.status = "limit_reached"
        run_record.completed_at = datetime.utcnow()
        run_record.step_history = step_history
        db.commit()

        return {
            "run_id": run_id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "status": "limit_reached",
            "response": "Agent completed maximum allowed step limit.",
            "steps": step_history
        }


agent_service = AgentService()
