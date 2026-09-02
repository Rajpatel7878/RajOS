"""
Agent Router - Routes user messages to the right specialized agent.
Priority order: Atlas → Nova → Sage → Echo → Pulse
"""

import re
from typing import Optional


class AgentRouter:
    """
    Routes user messages to the most appropriate agent based on intent keywords
    and message context. Falls back to Atlas for general conversation.
    """

    # Keyword patterns that trigger each specialist
    # NOTE: Order matters — checked top-to-bottom. Pulse must come before Sage
    # so "productivity report" routes to Pulse, not Sage.
    ROUTING_RULES = {
        "nova": [
            r"\b(search|find|look up|research|what is|who is|explain|summarize|document|read)\b",
            r"\b(knowledge|information|data|fact|detail|source|reference)\b",
        ],
        "pulse": [
            r"\b(analytics|stats|statistics|report|reports|insights?|trends?|usage|performance|metrics|kpi)\b",
            r"\b(how many|how often|activity|monitor|dashboard stats|productivity report|my stats)\b",
            r"\b(show me (my )?(stats|analytics|report|metrics|trends|activity|usage))\b",
        ],
        "sage": [
            r"\b(plan|planning|schedule|task|todo|to-do|project|goal|deadline|workflow)\b",
            r"\b(organize|prioritize|agenda|calendar|automate|automation)\b",
            r"\b(create task|add task|new task|track|progress|milestone)\b",
        ],
        "echo": [
            r"\b(remember|recall|memory|forget|store|save|profile|preference)\b",
            r"\b(what do you know|what did i|last time|previously|my name|my favorite|i told you)\b",
        ],
    }

    def route(self, message: str, requested_agent: Optional[str] = None) -> str:
        """
        Determine which agent should handle the message.

        Args:
            message: The user message
            requested_agent: Optional explicit agent selection from frontend

        Returns:
            agent_id string: one of 'atlas', 'nova', 'sage', 'echo', 'pulse'
        """
        # If user explicitly selected an agent, use it
        if requested_agent and requested_agent in ["atlas", "nova", "sage", "echo", "pulse"]:
            return requested_agent

        message_lower = message.lower()

        # Check routing rules in priority order
        for agent_id, patterns in self.ROUTING_RULES.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return agent_id

        # Default to Atlas for general conversation
        return "atlas"


def get_agent_instance(agent_id: str):
    """Instantiate and return the correct agent class."""
    from app.agents.atlas import Atlas
    from app.agents.nova import Nova
    from app.agents.sage import Sage
    from app.agents.echo import Echo
    from app.agents.pulse import Pulse

    agents = {
        "atlas": Atlas,
        "nova": Nova,
        "sage": Sage,
        "echo": Echo,
        "pulse": Pulse,
    }

    agent_class = agents.get(agent_id, Atlas)
    return agent_class()


def get_all_agents() -> list:
    """Return metadata for all available agents."""
    from app.agents.atlas import Atlas
    from app.agents.nova import Nova
    from app.agents.sage import Sage
    from app.agents.echo import Echo
    from app.agents.pulse import Pulse

    all_agents = [Atlas, Nova, Sage, Echo, Pulse]

    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "specialty": a.specialty,
            "tools": a.tools,
            "avatar": a.avatar,
            "status": "Active",
            "tasksCompleted": 0,
            "successRate": 98.5,
            "lastActive": "Now",
        }
        for a in all_agents
    ]
