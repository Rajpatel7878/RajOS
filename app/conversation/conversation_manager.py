from .conversation_engine import ConversationEngine
from .context_builder import ContextBuilder
from .history_manager import HistoryManager


class ConversationManager:

    def __init__(self):
        self.engine = ConversationEngine()
        self.context = ContextBuilder()
        self.history = HistoryManager()

    def chat(self, user_id, message):

        self.history.add(message)

        context = self.context.build(
            user_id,
            self.history.get()
        )

        return self.engine.process(
            message,
            context
        )
