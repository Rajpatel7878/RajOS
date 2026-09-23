import json
import re
from typing import Any, Dict, Optional, List

from app.memory.memory_engine import MemoryEngine
from app.agents.agent import Agent
from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config
from app.tools.tool_registry import tool_registry
from app.tools.tool_executor import tool_executor
from app.tools.tool_context import ToolExecutionContext
from app.tools.tool_result import ToolResult, ToolErrorCode

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


def ai_response(message: str, user=None, context=None, confirmation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = context or {}
    user_id = getattr(user, "id", 1) if user else 1

    exec_context = ToolExecutionContext(
        user_id=user_id,
        conversation_id=context.get("conversation_id"),
        permissions=["*"]
    )

    tool_execution_history: List[Dict[str, Any]] = []

    # Handle explicit confirmation callback from user
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
            tool_execution_history.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "result": res.to_dict()
            })

            prompt = f"""
You are RajOS AI. The user has explicitly confirmed executing the tool '{tool_name}'.
Tool Execution Result:
<UNTRUSTED_TOOL_RESULT tool="{tool_name}">
{json.dumps(res.to_dict(), default=str)}
</UNTRUSTED_TOOL_RESULT>

Instructions:
Synthesize a concise, friendly confirmation response for the user explaining the outcome.
"""
            provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")
            llm_res = llm_service.generate(prompt=prompt, provider=provider)
            return {
                "message": message,
                "response": llm_res.get("response", "Action completed."),
                "tool_executions": tool_execution_history
            }
        else:
            return {
                "message": message,
                "response": f"Action '{tool_name}' was cancelled by the user.",
                "tool_executions": []
            }

    # Standard tool calling loop
    agent = Agent()
    agent_result = agent.run(message, user, context)
    memories = memory_engine.get_relevant_memories(message)

    available_tools_schema = tool_registry.export_llm_schemas(permissions=["*"])
    tools_prompt_str = json.dumps(available_tools_schema, indent=2)

    rag_prompt = ""
    if context and isinstance(context, dict) and context.get("rag_context_prompt"):
        rag_prompt = f"\n\n{context['rag_context_prompt']}\n"

    conv_hist = context.get('conversation_history') if isinstance(context, dict) else context

    current_user_prompt = f"""
You are RajOS AI, a highly intelligent personal AI assistant.

Available Registered Tools:
{tools_prompt_str}

TOOL SELECTION RULES:
- Determine: Can I answer directly, or do I need a tool?
- If you require a tool to answer or perform an action requested by the user, respond ONLY with a JSON block:
```json
{{
  "tool_call": {{
    "name": "tool_name",
    "arguments": {{ ... }}
  }}
}}
```
- If NO tool is needed, provide your direct natural response.

User Message:
{message}

Conversation Context:
{conv_hist}

Relevant Memories:
{memories}
{rag_prompt}
"""

    provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    for round_num in range(MAX_TOOL_CALL_ROUNDS):
        llm_out = llm_service.generate(prompt=current_user_prompt, provider=provider)
        response_text = llm_out.get("response", "")

        tool_call = parse_tool_call_from_llm(response_text)

        if not tool_call:
            # Final natural language response from LLM
            return {
                "message": message,
                "memory_context": memories[:3],
                "agent": agent_result,
                "response": response_text,
                "tool_executions": tool_execution_history
            }

        # Tool execution requested by LLM
        t_name = tool_call["name"]
        t_args = tool_call.get("arguments", {})

        exec_res = tool_executor.execute(
            tool_name=t_name,
            arguments=t_args,
            context=exec_context
        )

        tool_execution_history.append({
            "tool_name": t_name,
            "arguments": t_args,
            "result": exec_res.to_dict()
        })

        if exec_res.requires_confirmation:
            # Pause execution and request user confirmation in chat UI
            return {
                "message": message,
                "requires_confirmation": True,
                "confirmation_details": {
                    "tool_name": t_name,
                    "arguments": t_args,
                    "confirmation_token": exec_res.confirmation_token,
                    "message": f"RajOS wants to perform destructive action: {t_name}"
                },
                "response": f"Confirmation required before executing '{t_name}'.",
                "tool_executions": tool_execution_history
            }

        # Feed tool result back to LLM context with prompt injection protection
        current_user_prompt += f"\n\nTool '{t_name}' Executed:\n<UNTRUSTED_TOOL_RESULT tool=\"{t_name}\">\n{json.dumps(exec_res.to_dict(), default=str)}\n</UNTRUSTED_TOOL_RESULT>\nNow generate your final clear answer to the user based on this tool result."

    # Max rounds reached
    return {
        "message": message,
        "memory_context": memories[:3],
        "agent": agent_result,
        "response": "Tool execution stopped safely after reaching max rounds.",
        "tool_executions": tool_execution_history
    }
