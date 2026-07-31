import chromadb


client = chromadb.PersistentClient(
    path="./vector_db"
)


collection = client.get_or_create_collection(
    name="rajOS_documents"
)


def add_document(
    doc_id: str,
    text: str,
    embedding: list
):

    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding]
    )


def search_document(
    embedding: list
):

    return collection.query(
        query_embeddings=[embedding],
        n_results=3
    )
