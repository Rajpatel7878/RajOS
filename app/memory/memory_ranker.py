class MemoryRanker:

    def rank(self, query, memories):

        query = query.lower().strip()

        query_words = set(query.split())

        ranked = []

        for memory in memories:

            score = 0

            key = str(memory.get("key", "")).lower()
            value = str(memory.get("value", "")).lower()

            if query == key:
                score += 10

            if query in key:
                score += 5

            if query in value:
                score += 8

            key_words = set(key.split())
            value_words = set(value.split())

            score += len(query_words & key_words) * 2
            score += len(query_words & value_words) * 3

            if isinstance(memory.get("importance"), str):
                importance = memory["importance"].lower()

                if importance == "high":
                    score += 5
                elif importance == "medium":
                    score += 3
                elif importance == "low":
                    score += 1

            ranked.append({
                "score": score,
                **memory
            })

        ranked.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return ranked
