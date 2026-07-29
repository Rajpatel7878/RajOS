from app.database.connection import SessionLocal
from app.models.memory import Memory
from app.agents.agent import Agent


def get_user_memory():
    db = SessionLocal()

    memories = db.query(Memory).all()

    db.close()

    return [
        {
            "key": memory.key,
            "value": memory.value
        }
        for memory in memories
    ]


def ai_response(message: str):

    memories = get_user_memory()

    context = "\n".join(
        f"{memory['key']}: {memory['value']}"
        for memory in memories
    )

    agent = Agent()

    result = agent.run(message)

    return {
        "message": message,
        "memory_context": context,
        "agent": result,
        "response": "RajOS AI Agent completed the request successfully."
    }
