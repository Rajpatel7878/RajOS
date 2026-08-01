from fastapi import APIRouter

from app.rag.rag_service import rag_service
from app.rag.rag_schemas import (
    KnowledgeAddRequest,
    RAGQueryRequest
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG Knowledge"]
)


@router.post("/add")
def add_knowledge(
    request: KnowledgeAddRequest
):

    return rag_service.add_knowledge(
        request.doc_id,
        request.content
    )



@router.post("/query")
def query_knowledge(
    request: RAGQueryRequest
):

    return rag_service.query(
        request.question
    )
