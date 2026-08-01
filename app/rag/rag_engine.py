from app.rag.document_processor import process_document
from app.rag.embeddings import create_embedding
from app.rag.vector_store import add_document, search_document


class RAGEngine:


    def add_knowledge(
        self,
        doc_id: str,
        content: str
    ):

        processed = process_document(content)

        results = []

        for index, chunk in enumerate(
            processed["chunks"]
        ):

            embedding = create_embedding(
                chunk
            )

            chunk_id = f"{doc_id}_{index}"

            add_document(
                chunk_id,
                chunk,
                embedding
            )

            results.append(chunk_id)


        return {
            "status": "success",
            "document_id": doc_id,
            "chunks_added": len(results),
            "chunk_ids": results
        }



    def query(
        self,
        question: str
    ):

        embedding = create_embedding(
            question
        )

        results = search_document(
            embedding
        )

        return {
            "query": question,
            "results": results
        }



rag_engine = RAGEngine()
