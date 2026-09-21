from app.services.profile_query import ProfileQuery
from app.services.preference_query import PreferenceQuery
from app.memory.memory_service import memory_service


class ContextBuilder:
    """Builds unified LLM prompt context with context-window limits and Phase 4 Memory 2.0 integration."""

    def __init__(self):
        self.profile_query = ProfileQuery()
        self.preference_query = PreferenceQuery()

    def build(
        self,
        db,
        user_id: int,
        query_text: str = "",
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

        # Retrieve isolated memories strictly for user_id with failure isolation
        user_memories = []
        try:
            user_memories = memory_service.get_relevant_memories_for_context(
                db=db,
                user_id=user_id,
                query_text=query_text or "",
                limit=5
            )
        except Exception as e:
            print(f"[ContextBuilder] Failure retrieving memories (isolated): {e}")

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
            "memory": user_memories if user_memories else (memory_data or []),
            "conversation_history": formatted_history,
            "semantic_memory": user_memories,
            "rag_documents": [],
            "tool_context": []
        }

        return context
