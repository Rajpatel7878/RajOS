from app.agents.planner import Planner
from app.agents.tool_manager import ToolManager
from app.tools.tool_registry import ToolRegistry


class Agent:

    def __init__(self):
        self.planner = Planner()
        self.tool_manager = ToolManager()
        self.registry = ToolRegistry()

    def run(self, user_input: str):

        tool = self.tool_manager.select_tool(user_input)

        plan = self.planner.create_plan(user_input)

        tool_result = self.registry.execute(tool, user_input)

        return {
            "tool_selected": tool,
            "plan": plan,
            "tool_result": tool_result,
            "status": "Agent executed successfully"
        }
