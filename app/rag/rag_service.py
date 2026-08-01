from app.rag.rag_engine import rag_engine


class RAGService:


    def add_knowledge(
        self,
        doc_id: str,
        content: str
    ):

        return rag_engine.add_knowledge(
            doc_id,
            content
        )



    def query(
        self,
        question: str
    ):

        return rag_engine.query(
            question
        )



rag_service = RAGService()
