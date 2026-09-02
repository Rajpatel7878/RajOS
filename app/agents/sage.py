"""
Sage - Planning & Productivity Agent
Manages tasks, schedules, and workflow automation.
"""

from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config


class Sage:
    """
    Sage specializes in planning and productivity. It helps users organize tasks,
    create schedules, set priorities, and design efficient workflows.
    """

    id = "sage"
    name = "Sage"
    description = "Planning & productivity specialist. Manages tasks, schedules, and workflows."
    specialty = "Planning & Productivity"
    tools = ["task_manager", "calendar", "workflow_builder", "prioritizer"]
    avatar = "S"

    SYSTEM_PROMPT = """You are Sage, the Planning & Productivity agent of RajOS.
You are organized, strategic, and methodical. You help users plan effectively.

Your capabilities:
- Break down projects into actionable tasks with deadlines
- Create structured plans and workflows
- Prioritize tasks by impact and urgency (using Eisenhower Matrix)
- Suggest productivity strategies and time management techniques
- Design automation workflows to save time
- Track progress and identify bottlenecks

Always provide practical, actionable advice with clear next steps."""

    def __init__(self):
        self.provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    def run(self, message: str, context: dict = None) -> dict:
        """Run Sage for planning and productivity tasks."""
        context = context or {}

        existing_tasks = context.get("tasks", [])

        prompt = f"""{self.SYSTEM_PROMPT}

Current Tasks: {existing_tasks}
Conversation Context: {context.get("conversation_history", [])}

Planning Request: {message}

Provide a structured, actionable plan:"""

        result = llm_service.generate(prompt=prompt, provider=self.provider)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "response": result.get("response", "Let me help you create a plan. What are your goals and timeline?"),
            "status": "completed",
            "steps": [
                {"label": "Analyzed request and goals", "status": "done"},
                {"label": "Reviewed existing tasks", "status": "done", "tool": "task_manager"},
                {"label": "Created structured plan", "status": "done"},
            ],
        }
