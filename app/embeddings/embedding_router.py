from fastapi import APIRouter

from app.embeddings.embedding_service import embedding_service
from app.embeddings.embedding_schemas import (
    EmbeddingRequest,
    EmbeddingResponse
)


router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"]
)


@router.post(
    "/generate",
    response_model=EmbeddingResponse
)
def generate_embedding(
    request: EmbeddingRequest
):

    embedding = embedding_service.generate_embedding(
        request.text
    )

    return {
        "embedding": embedding,
        "dimensions": len(embedding)
    }
