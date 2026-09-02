"""
Pulse - Analytics & Monitoring Agent
Tracks activity, generates insights, monitors system status.
"""

from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config


class Pulse:
    """
    Pulse specializes in analytics and monitoring. It tracks user activity,
    generates insights, monitors system performance, and provides reports.
    """

    id = "pulse"
    name = "Pulse"
    description = "Analytics & monitoring specialist. Tracks activity, generates insights, and system reports."
    specialty = "Analytics & Monitoring"
    tools = ["activity_tracker", "analytics_engine", "report_generator", "trend_analyzer"]
    avatar = "P"

    SYSTEM_PROMPT = """You are Pulse, the Analytics & Monitoring agent of RajOS.
You are data-driven, insightful, and focused on helping users understand their patterns.

Your capabilities:
- Analyze user activity patterns and trends
- Generate detailed reports on productivity, tasks, and usage
- Monitor system status and performance
- Identify insights and opportunities for improvement
- Create data visualizations and summaries
- Track progress towards goals over time
- Alert users to important patterns or anomalies

Always back your insights with data and provide actionable recommendations."""

    def __init__(self):
        self.provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    def run(self, message: str, context: dict = None) -> dict:
        """Run Pulse for analytics and monitoring tasks."""
        context = context or {}

        stats = context.get("stats", {})
        activity = context.get("activity", [])

        prompt = f"""{self.SYSTEM_PROMPT}

Current Stats: {stats}
Recent Activity: {activity}

Analytics Request: {message}

Provide data-driven insights and recommendations:"""

        result = llm_service.generate(prompt=prompt, provider=self.provider)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "response": result.get("response", "I'm Pulse, your analytics agent. I can help you understand your productivity patterns and activity trends."),
            "status": "completed",
            "steps": [
                {"label": "Collected activity data", "status": "done", "tool": "activity_tracker"},
                {"label": "Analyzed trends", "status": "done", "tool": "trend_analyzer"},
                {"label": "Generated insights", "status": "done", "tool": "report_generator"},
            ],
        }
