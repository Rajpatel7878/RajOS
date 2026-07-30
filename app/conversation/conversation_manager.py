from .conversation_engine import ConversationEngine
from .context_builder import ContextBuilder


class ConversationManager:

    def __init__(self):
        self.engine = ConversationEngine()
        self.context = ContextBuilder()


    def chat(self, user_id, message, history):

        context = self.context.build(
            user_id,
            history
        )

        return self.engine.process(
            message,
            context
        )
