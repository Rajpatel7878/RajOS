import re

def highlight(text: str, query: str) -> str:
    if not text:
        return ""

    pattern = re.compile(
        re.escape(query),
        re.IGNORECASE
    )

    return pattern.sub(
        lambda m: f"<mark>{m.group(0)}</mark>",
        text
    )
