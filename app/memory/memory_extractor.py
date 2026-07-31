class MemoryExtractor:

    def extract(self, message):

        text = message.lower()

        category = "general"

        if any(word in text for word in [
            "building",
            "project",
            "developing",
            "creating"
        ]):
            category = "project"

        elif any(word in text for word in [
            "learning",
            "learn",
            "using",
            "python",
            "fastapi",
            "ai"
        ]):
            category = "skill"

        elif any(word in text for word in [
            "like",
            "prefer",
            "love"
        ]):
            category = "preference"

        elif any(word in text for word in [
            "goal",
            "want",
            "aim"
        ]):
            category = "goal"


        return [{
            "memory": message,
            "category": category,
            "importance": "medium"
        }]
