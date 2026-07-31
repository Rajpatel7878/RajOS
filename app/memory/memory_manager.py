from .memory_extractor import MemoryExtractor
from .memory_classifier import MemoryClassifier


class MemoryManager:

    def __init__(self):
        self.extractor = MemoryExtractor()
        self.classifier = MemoryClassifier()


    def process(self, message):

        memories = self.extractor.extract(message)

        result = []

        for memory in memories:
            result.append(
                self.classifier.classify(memory)
            )

        return result
