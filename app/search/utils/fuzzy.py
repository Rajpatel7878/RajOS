from rapidfuzz import fuzz

def fuzzy_score(text: str, query: str) -> int:
    if not text:
        return 0

    return fuzz.partial_ratio(
        query.lower(),
        text.lower()
    )
