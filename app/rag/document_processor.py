def split_text(
    text: str,
    chunk_size: int = 500
):

    chunks = []

    words = text.split()

    for i in range(
        0,
        len(words),
        chunk_size
    ):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


def process_document(content: str):

    chunks = split_text(content)

    return {
        "total_chunks": len(chunks),
        "chunks": chunks
    }
