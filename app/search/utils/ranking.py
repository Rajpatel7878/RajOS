from app.search.utils.fuzzy import fuzzy_score

def calculate_score(text: str, query: str) -> int:
    text = (text or "").lower()
    query = query.lower()

    score = 0

    if text == query:
        score += 100

    elif text.startswith(query):
        score += 80

    elif query in text:
        score += 60

    score += fuzzy_score(text, query)

    return score
