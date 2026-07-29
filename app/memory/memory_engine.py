from app.memory.memory_store import MemoryStore
from app.memory.memory_retriever import MemoryRetriever
from app.memory.memory_ranker import MemoryRanker
from app.memory.memory_manager import MemoryManager


class MemoryEngine:

    def __init__(self):
        self.store = MemoryStore()
        self.retriever = MemoryRetriever()
        self.ranker = MemoryRanker()
        self.manager = MemoryManager()


    def save_memory(self, key, value):
        return self.store.save(key, value)


    def process_memory(self, message):

        memories = self.manager.process(message)

        saved = []

        for memory in memories:

            self.store.save(
                memory["category"],
                memory
            )

            saved.append(memory)

        return saved


    def get_relevant_memories(self, query):

        memories = self.retriever.get_all()

        ranked = self.ranker.rank(
            query,
            memories
        )

        return ranked


    def remember(self, key, value):

        self.save_memory(key, value)

        return self.get_relevant_memories(value)
