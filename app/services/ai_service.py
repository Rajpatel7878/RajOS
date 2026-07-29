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

    return {
        "message": message,
        "memory_context": memories[:3],
        "agent": agent_result,
        "response": "AI assistant is ready with intelligent memory."
    }
