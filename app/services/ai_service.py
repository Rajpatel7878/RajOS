from app.memory.memory_engine import MemoryEngine
from app.agents.agent import Agent
from app.llm.llm_service import llm_service
from app.llm.llm_config import llm_config

memory_engine = MemoryEngine()


def ai_response(message: str, user=None, context=None):

    agent = Agent()
    agent_result = agent.run(message, user, context)

    memories = memory_engine.get_relevant_memories(message)

    prompt = f"""
You are RajOS AI, a highly intelligent personal AI assistant.

User Message:
{message}

Conversation Context:
{context}

Relevant Memories:
{memories}

Instructions:
- Answer naturally like ChatGPT.
- Use memories only if relevant.
- Do not always mention memories.
- Be conversational, helpful and accurate.
"""

    provider = getattr(llm_config, "DEFAULT_PROVIDER", "gemini")

    llm = llm_service.generate(
        prompt=prompt,
        provider=provider
    )

    return {
        "message": message,
        "memory_context": memories[:3],
        "agent": agent_result,
        "response": llm.get("response", "No response generated.")
    }
