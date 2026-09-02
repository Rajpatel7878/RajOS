"""
Atlas - General Conversation & Task Orchestrator
The primary AI assistant agent. Routes to specialists when needed.
"""

from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config


class Atlas:
    """
    Atlas is the primary orchestrator agent. It handles general conversation,
    decides when to delegate to specialist agents, and manages multi-step tasks.
    """

    id = "atlas"
    name = "Atlas"
    description = "General AI assistant and task orchestrator. Routes to specialist agents when needed."
    specialty = "General Conversation & Orchestration"
    tools = ["memory", "task_manager", "agent_router", "context_builder"]
    avatar = "A"

    SYSTEM_PROMPT = """You are Atlas, the primary AI assistant of RajOS.
You are intelligent, helpful, and conversational. You handle general questions,
orchestrate complex multi-step tasks, and delegate to specialist agents when needed.

Your capabilities:
- Answer any question clearly and accurately
- Break down complex tasks into steps  
- Remember context from the conversation
- Know when to delegate: research → Nova, planning → Sage, memory → Echo, analytics → Pulse

Always respond naturally and helpfully."""

    def __init__(self):
        self.provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    def run(self, message: str, context: dict = None) -> dict:
        """Run Atlas on a user message."""
        context = context or {}

        prompt = f"""{self.SYSTEM_PROMPT}

Conversation Context:
{context.get("conversation_history", [])}

Relevant Memories:
{context.get("memories", [])}

User Message: {message}

Respond helpfully and naturally:"""

        result = llm_service.generate(prompt=prompt, provider=self.provider)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "response": result.get("response", "I'm here to help. What would you like to do?"),
            "status": "completed",
            "steps": [
                {"label": "Analyzed user intent", "status": "done"},
                {"label": "Retrieved context", "status": "done"},
                {"label": "Generated response", "status": "done"},
            ],
        }
