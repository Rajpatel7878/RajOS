from app.services.profile_query import ProfileQuery
from app.services.preference_query import PreferenceQuery
from app.memory.memory_service import memory_service
from app.rag.knowledge_service import knowledge_service


class ContextBuilder:
    """Builds unified LLM prompt context with context-window limits, Memory 2.0, and Knowledge RAG 2.0 integration."""

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

        # 1. Retrieve isolated Memory 2.0 context for user_id with failure isolation
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

        # 2. Retrieve isolated Knowledge RAG 2.0 context for user_id with failure isolation
        rag_hits = []
        rag_context_prompt = ""
        rag_citations = []
        try:
            if query_text:
                rag_hits, rag_context_prompt, rag_citations = knowledge_service.build_knowledge_context(
                    db=db,
                    user_id=user_id,
                    query_text=query_text
                )
        except Exception as e:
            print(f"[ContextBuilder] Failure retrieving knowledge RAG context (isolated): {e}")

        # 3. Format conversation history: cap at last 20 messages, preserve role formatting
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
            "rag_documents": rag_hits,
            "rag_context_prompt": rag_context_prompt,
            "rag_sources": rag_citations,
            "tool_context": []
        }

        return context
