from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.decision_engine import DecisionEngine
from app.agents.tool_manager import ToolManager

from app.tools.tool_registry import ToolRegistry
from app.tools.tool_executor import ToolExecutor

from app.resolver.reference_resolver import ReferenceResolver


class Agent:

    def __init__(self):

        self.decision_engine = DecisionEngine()
        self.planner = Planner()
        self.executor = Executor()
        self.tool_manager = ToolManager()

        self.registry = ToolRegistry()
        self.tool_executor = ToolExecutor()

        self.resolver = ReferenceResolver()


    def run(
        self,
        user_input: str,
        user=None,
        context=None
    ):

        context = context or {}


        reference_context = context.get(
            "context",
            context
        ) if context else {}


        reference = self.resolver.resolve(
            user_input,
            reference_context
        )



        decision = self.decision_engine.decide(
            user_input
        )


        if reference["has_reference"]:

            if reference["type"] == "note":

                decision["intent"] = "note_reference"
                decision["action"] = "retrieve_note"


            elif reference["type"] == "task":

                decision["intent"] = "task_reference"
                decision["action"] = "retrieve_task"



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
        tool_found = False

        if tool_name:

            tool = self.registry.get_tool(
                tool_name
            )

            if tool:
                tool_found = True

                tool_result = self.tool_executor.execute(
                    tool,
                    {
                        "message": user_input,
                        "user": user,
                        "reference": reference
                    }
                )

        return {
            "decision": decision,
            "reference": reference,
            "plan": plan,
            "execution": execution,
            "tool_selected": tool_name,
            "tool_found": tool_found,
            "steps_executed": len(plan.get("steps", [])),
            "agent_version": "v1",
            "tool_result": tool_result,
            "status": "Agent executed successfully"
        }
