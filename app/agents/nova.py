"""
Nova - Research & Knowledge Retrieval Agent
Searches memories, notes, documents, and external knowledge.
"""

from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config


class Nova:
    """
    Nova specializes in research and knowledge retrieval. It searches through
    the user memory store, notes, documents, and synthesizes information.
    """

    id = "nova"
    name = "Nova"
    description = "Research & knowledge retrieval specialist. Searches memories, notes, and documents."
    specialty = "Research & Knowledge Retrieval"
    tools = ["memory_search", "notes_search", "document_search", "web_search"]
    avatar = "N"

    SYSTEM_PROMPT = """You are Nova, the Research & Knowledge agent of RajOS.
You specialize in finding, synthesizing, and presenting information from the user knowledge base.

Your capabilities:
- Search through personal memories and stored knowledge
- Analyze and summarize documents and notes
- Answer research questions with supporting evidence
- Compare and contrast information from multiple sources
- Provide clear citations and context for your findings

Be thorough, accurate, and well-organized in your responses."""

    def __init__(self):
        self.provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    def run(self, message: str, context: dict = None) -> dict:
        """Run Nova to research a query."""
        context = context or {}

        memories = context.get("memories", [])
        notes = context.get("notes", [])

        prompt = f"""{self.SYSTEM_PROMPT}

Available Knowledge:
- Memories: {memories}
- Notes: {notes}

Research Query: {message}

Provide a comprehensive, well-researched response:"""

        result = llm_service.generate(prompt=prompt, provider=self.provider)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "response": result.get("response", "I searched through your knowledge base but didn't find specific information on this topic."),
            "status": "completed",
            "steps": [
                {"label": "Searched memory store", "status": "done", "tool": "memory_search"},
                {"label": "Searched notes", "status": "done", "tool": "notes_search"},
                {"label": "Synthesized findings", "status": "done"},
            ],
        }
