from app.services.profile_query import ProfileQuery
from app.services.preference_query import PreferenceQuery
from app.memory.memory_retriever import MemoryRetriever


class ContextBuilder:
    """Builds unified LLM prompt context with context-window limits and Phase 4-6 extension points."""

    def __init__(self):
        self.profile_query = ProfileQuery()
        self.preference_query = PreferenceQuery()
        self.memory_retriever = MemoryRetriever()

    def build(
        self,
        db,
        user_id: int,
        memory_data=None,
        conversation_history=None
    ):
        profile = {
            "name": self.profile_query.get_profile(
                db,
                user_id,
                "name"
            )
        }

        preferences = self.preference_query.get_all_preferences(
            db,
            user_id
        )

        # Retrieve static/rule-based memory
        memories = self.memory_retriever.get_all()

        # Format conversation history: cap at last 20 messages, preserve role formatting
        formatted_history = []
        if conversation_history:
            recent_items = conversation_history[-20:]
            for item in recent_items:
                if isinstance(item, dict):
                    role = item.get("role", "user").capitalize()
                    content = item.get("content", "")
                    formatted_history.append(f"{role}: {content}")
                elif hasattr(item, "role") and hasattr(item, "content"):
                    role = item.role.capitalize()
                    formatted_history.append(f"{role}: {item.content}")
                else:
                    formatted_history.append(str(item))

        context = {
            "user_id": user_id,
            "profile": profile,
            "preferences": preferences,
            "memory": memories if memories else (memory_data or []),
            "conversation_history": formatted_history,
            # Phase 4 Extension Point: Semantic Memory
            "semantic_memory": [],
            # Phase 5 Extension Point: RAG Knowledge Documents
            "rag_documents": [],
            # Phase 6 Extension Point: Tool Execution Context
            "tool_context": []
        }

        return context
