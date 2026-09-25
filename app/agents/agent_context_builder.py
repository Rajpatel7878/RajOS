import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.agent import AgentDefinitionModel
from app.tools.tool_registry import tool_registry
from app.memory.memory_service import memory_service
from app.rag.knowledge_service import KnowledgeService

knowledge_service = KnowledgeService()


class AgentContextBuilder:

    def build_prompt(
        self,
        db: Session,
        agent: AgentDefinitionModel,
        user_id: int,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        step_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Assembles prompt enforcing agent instructions, tool restrictions, memory policy, and RAG access."""

        # 1. Filter allowed tool schemas
        all_schemas = tool_registry.export_llm_schemas(permissions=["*"])
        allowed_tool_schemas = [
            schema for schema in all_schemas
            if schema["name"] in agent.allowed_tools
        ]
        tools_json_str = json.dumps(allowed_tool_schemas, indent=2)

        # 2. Memory context (honoring memory_policy)
        memory_str = "None (Memory access disabled for this agent)"
        if agent.memory_policy in ["read", "read_write"]:
            try:
                memories = memory_service.get_memories(
                    db=db,
                    user_id=user_id,
                    search_query=user_prompt,
                    status="active"
                )
                if memories:
                    mem_list = [{"key": m.key, "value": m.value, "type": m.memory_type} for m in memories[:3]]
                    memory_str = json.dumps(mem_list)
            except Exception:
                memory_str = "None"

        # 3. Knowledge / RAG context (honoring knowledge_access)
        rag_str = ""
        if agent.knowledge_access in ["search", "full"]:
            try:
                knowledge_results = knowledge_service.search_knowledge(
                    db=db,
                    user_id=user_id,
                    query_text=user_prompt,
                    limit=3
                )
                if knowledge_results:
                    rag_docs = [
                        f"- Document: {r.get('filename')}\n  Snippet: {r.get('chunk_text', '')[:250]}"
                        for r in knowledge_results
                    ]
                    rag_str = "\nRelevant Knowledge Base Documents:\n" + "\n".join(rag_docs)
            except Exception:
                rag_str = ""

        # 4. Step History / Tool Executions
        history_str = ""
        if step_history and len(step_history) > 0:
            formatted_steps = []
            for step in step_history:
                t_name = step.get("tool_name")
                t_args = step.get("arguments")
                t_res = step.get("result")
                formatted_steps.append(
                    f"Step {step.get('step')}: Executed Tool '{t_name}' with args {json.dumps(t_args)}\n"
                    f"<UNTRUSTED_TOOL_RESULT tool=\"{t_name}\">\n{json.dumps(t_res, default=str)}\n</UNTRUSTED_TOOL_RESULT>"
                )
            history_str = "\n\nPrevious Step Execution History:\n" + "\n\n".join(formatted_steps)

        # 5. Conversation History
        conv_str = ""
        if conversation_history:
            recent_turns = [
                f"{(m.get('role', 'user') if isinstance(m, dict) else 'User').capitalize()}: {m.get('content', str(m)) if isinstance(m, dict) else str(m)}"
                for m in conversation_history[-6:]
            ]
            conv_str = "\nRecent Conversation History:\n" + "\n".join(recent_turns)

        # 6. Assemble Final Prompt
        prompt = f"""
Agent Persona & Instructions:
{agent.system_instructions}

Allowed Capabilities: {json.dumps(agent.capabilities)}
Allowed Registered Tools:
{tools_json_str}

TOOL SELECTION RULES:
- If a tool is required to fulfill the user's request, respond ONLY with a JSON block:
```json
{{
  "tool_call": {{
    "name": "tool_name",
    "arguments": {{ ... }}
  }}
}}
```
- Only call tools that are listed in the Allowed Registered Tools above.
- If no tool is needed or if tool results provide enough information, provide your final helpful natural language response.

User Input:
{user_prompt}
{conv_str}

Relevant Memories:
{memory_str}
{rag_str}
{history_str}
"""
        return prompt.strip()


agent_context_builder = AgentContextBuilder()
