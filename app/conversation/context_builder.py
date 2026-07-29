class ContextBuilder:

    def build(self, user_id, history=None):
        return {
            "user_id": user_id,
            "history": history or []
        }
