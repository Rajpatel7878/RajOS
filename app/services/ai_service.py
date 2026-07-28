import app.models

from app.database.connection import SessionLocal
from app.models.memory import Memory

from app.rag.embeddings import create_embedding
from app.rag.vector_store import search_document


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


def get_document_context(message: str):

    embedding = create_embedding(message)

    results = search_document(
        embedding
    )

    context = ""

    if results.get("documents"):

        for doc in results["documents"][0]:
            context += doc + "\n"

    return context


def ai_response(message: str):

    memories = get_user_memory()

    memory_context = ""

    for memory in memories:
        memory_context += (
            f"{memory['key']}: "
            f"{memory['value']}\n"
        )

    document_context = get_document_context(
        message
    )

    return {
        "message": message,
        "memory_context": memory_context,
        "document_context": document_context,
        "response": "AI assistant is ready with knowledge retrieval"
    }
