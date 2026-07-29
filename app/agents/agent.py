from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.tool_manager import ToolManager


class Agent:

    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()
        self.tool_manager = ToolManager()

    def run(self, user_input: str):

        tool = self.tool_manager.select_tool(user_input)

        plan = self.planner.create_plan(user_input)

        result = self.executor.execute(plan)

        return {
            "tool_selected": tool,
            "plan": plan,
            "execution": result,
            "status": "Agent completed successfully"
        }
