from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.decision_engine import DecisionEngine
from app.agents.tool_manager import ToolManager
from app.tools.tool_registry import ToolRegistry


class Agent:

    def __init__(self):

        self.decision_engine = DecisionEngine()
        self.planner = Planner()
        self.executor = Executor()
        self.tool_manager = ToolManager()
        self.registry = ToolRegistry()


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

        tool = self.tool_manager.select_tool(
            user_input
        )

        tool_result = self.registry.execute(
            tool,
            user_input
        )


        return {
            "decision": decision,
            "plan": plan,
            "execution": execution,
            "tool_selected": tool,
            "tool_result": tool_result,
            "status": "Agent executed successfully"
        }
