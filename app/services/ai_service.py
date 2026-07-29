from app.memory.memory_engine import MemoryEngine
from app.agents.agent import Agent


memory_engine = MemoryEngine()
agent = Agent()


def ai_response(message: str):

    memories = memory_engine.get_relevant_memories(message)

    agent_result = agent.run(message)

    return {
        "message": message,
        "memory_context": memories[:3],
        "agent": agent_result,
        "response": "AI assistant is ready with intelligent memory."
    }
