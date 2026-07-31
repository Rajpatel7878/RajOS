from app.services.profile_query import ProfileQuery
from app.services.preference_query import PreferenceQuery
from app.memory.memory_retriever import MemoryRetriever


class ContextBuilder:

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

        memories = self.memory_retriever.get_all()

        context = {
            "user_id": user_id,
            "profile": profile,
            "preferences": preferences,
            "memory": memories if memories else (memory_data or []),
            "conversation_history": conversation_history or []
        }

        return context
