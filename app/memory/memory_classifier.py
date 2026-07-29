class MemoryClassifier:

    def classify(self, memory):

        category = memory["category"]

        if category in [
            "project",
            "goal"
        ]:
            memory["importance"] = "high"

        elif category in [
            "preference",
            "skill"
        ]:
            memory["importance"] = "medium"

        else:
            memory["importance"] = "low"

        return memory
