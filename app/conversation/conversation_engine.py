class ConversationEngine:

    def process(self, message, context=None):
        return {
            "input": message,
            "context": context or {},
            "response": f"RajOS understood: {message}"
        }
