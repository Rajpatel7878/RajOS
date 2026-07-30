from app.memory.memory_engine import MemoryEngine
from app.agents.agent import Agent


memory_engine = MemoryEngine()


def ai_response(
    message: str,
    user=None
):

    agent = Agent()

    memories = memory_engine.get_relevant_memories(message)

    agent_result = agent.run(
        message,
        user
    )

    response = "I understood your request."

    tool_result = agent_result.get("tool_result")

    if tool_result and tool_result.get("status") == "success":

        result = tool_result.get("result", {})

        tool = result.get("tool")

        if tool == "productivity":

            analysis = result.get("analysis", {})
            score = result.get("score", {})

            response = (
                f"📊 Productivity Report\n\n"
                f"Completed Tasks: {analysis.get('completed_tasks',0)}/{analysis.get('total_tasks',0)}\n"
                f"Pending Tasks: {analysis.get('pending_tasks',0)}\n"
                f"Productivity Score: {score.get('score',0)}%\n"
                f"Level: {score.get('level','unknown')}"
            )

        elif tool == "notes":

            if "notes" in result:

                response = (
                    f"📝 I found {result.get('count',0)} notes in your account."
                )

            else:

                response = (
                    f"✅ Your note has been saved successfully.\n\n"
                    f"Title: {result.get('title')}\n"
                    f"Content: {result.get('content')}"
                )

        elif tool == "tasks":

            response = "✅ Task operation completed successfully."

        elif tool == "memory":

            response = "🧠 Memory updated successfully."

        elif tool == "documents":

            response = "📄 Document processed successfully."

    elif memories:

        response = (
            f"I found {len(memories[:3])} relevant memories related to your request."
        )

    return {
        "message": message,
        "memory_context": memories[:3],
        "agent": agent_result,
        "response": response
    }
