class MemoryRanker:

    def rank(self, query, memories):

        query = query.lower()

        ranked = []

        for memory in memories:

            score = 0

            if query in memory["key"].lower():
                score += 2

            if query in memory["value"].lower():
                score += 3

            ranked.append({
                "score": score,
                **memory
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        return ranked
