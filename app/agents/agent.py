from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.decision_engine import DecisionEngine
from app.agents.tool_manager import ToolManager

from app.tools.tool_registry import ToolRegistry
from app.tools.tool_executor import ToolExecutor


class Agent:

    def __init__(self):

        self.decision_engine = DecisionEngine()
        self.planner = Planner()
        self.executor = Executor()
        self.tool_manager = ToolManager()

        self.registry = ToolRegistry()
        self.tool_executor = ToolExecutor()


    def run(self, user_input: str):

        decision = self.decision_engine.decide(
            user_input
        )


        plan = self.planner.create_plan(
            user_input,
            decision["intent"]
        )


        execution = self.executor.execute(
            plan
        )


        tool_name = self.tool_manager.select_tool(
            user_input
        )


        tool_result = None


        if tool_name:

            tool = self.registry.get_tool(
                tool_name
            )

            tool_result = self.tool_executor.execute(
                tool,
                user_input
            )


        return {
            "decision": decision,
            "plan": plan,
            "execution": execution,
            "tool_selected": tool_name,
            "tool_result": tool_result,
            "status": "Agent executed successfully"
        }
