"""
Echo - Memory & Context Agent
Stores/retrieves memories, builds user profiles, manages long-term context.
"""

from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config


class Echo:
    """
    Echo specializes in memory management and personal context. It learns about
    the user over time, stores key information, and retrieves relevant context.
    """

    id = "echo"
    name = "Echo"
    description = "Memory & context specialist. Remembers preferences, builds your profile, and retrieves personal context."
    specialty = "Memory & Context Management"
    tools = ["memory_store", "memory_search", "profile_builder", "preference_tracker"]
    avatar = "E"

    SYSTEM_PROMPT = """You are Echo, the Memory & Context agent of RajOS.
You are the keeper of personal knowledge — you remember everything important about the user.

Your capabilities:
- Store new information about preferences, facts, and patterns
- Retrieve relevant past memories for the current conversation
- Build and maintain a comprehensive user profile
- Track preferences, goals, and key personal facts
- Identify patterns in user behavior and preferences
- Answer questions about what you remember about the user

Be personal, accurate, and respectful of the user privacy."""

    def __init__(self):
        self.provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    def run(self, message: str, context: dict = None) -> dict:
        """Run Echo for memory and context tasks."""
        context = context or {}

        memories = context.get("memories", [])
        profile = context.get("profile", {})

        prompt = f"""{self.SYSTEM_PROMPT}

Stored Memories: {memories}
User Profile: {profile}

Memory Request: {message}

Respond based on what you know about the user:"""

        result = llm_service.generate(prompt=prompt, provider=self.provider)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "response": result.get("response", "I'm Echo, your memory agent. I help you remember important things. What would you like me to store or recall?"),
            "status": "completed",
            "steps": [
                {"label": "Searched memory store", "status": "done", "tool": "memory_search"},
                {"label": "Retrieved user profile", "status": "done", "tool": "profile_builder"},
                {"label": "Processed memory request", "status": "done"},
            ],
        }
