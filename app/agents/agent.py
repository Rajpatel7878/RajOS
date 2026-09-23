from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.decision_engine import DecisionEngine
from app.agents.tool_manager import ToolManager

from app.tools.tool_registry import tool_registry, ToolRegistry
from app.tools.tool_executor import tool_executor, ToolExecutor
from app.tools.tool_context import ToolExecutionContext

from app.resolver.reference_resolver import ReferenceResolver


class Agent:

    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.planner = Planner()
        self.executor = Executor()
        self.tool_manager = ToolManager()

        self.registry = tool_registry
        self.tool_executor = tool_executor

        self.resolver = ReferenceResolver()

    def run(
        self,
        user_input: str,
        user=None,
        context=None
    ):
        context = context or {}
        user_id = getattr(user, "id", 1) if user else 1

        exec_context = ToolExecutionContext(
            user_id=user_id,
            conversation_id=context.get("conversation_id"),
            permissions=["*"]
        )

        reference_context = context.get("context", context) if context else {}
        reference = self.resolver.resolve(user_input, reference_context)

        decision = self.decision_engine.decide(user_input)

        if reference.get("has_reference"):
            if reference.get("type") == "note":
                decision["intent"] = "note_reference"
                decision["action"] = "retrieve_note"
            elif reference.get("type") == "task":
                decision["intent"] = "task_reference"
                decision["action"] = "retrieve_task"

        plan = self.planner.create_plan(user_input, decision["intent"])
        execution = self.executor.execute(plan)

        tool_name = self.tool_manager.select_tool(user_input)
        tool_result = None
        tool_found = False

        if tool_name:
            tool = self.registry.get_tool(tool_name)
            if tool:
                tool_found = True
                tool_result = self.tool_executor.execute(
                    tool_name=tool_name,
                    arguments={"message": user_input},
                    context=exec_context
                ).to_dict()

        return {
            "decision": decision,
            "reference": reference,
            "plan": plan,
            "execution": execution,
            "tool_selected": tool_name,
            "tool_found": tool_found,
            "steps_executed": len(plan.get("steps", [])),
            "agent_version": "v2",
            "tool_result": tool_result,
            "status": "Agent executed successfully"
        }
