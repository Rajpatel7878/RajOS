from fastapi import APIRouter

from app.llm.llm_service import llm_service
from app.llm.llm_schemas import (
    LLMRequest,
    LLMResponse
)


router = APIRouter(
    prefix="/llm",
    tags=["LLM"]
)


@router.post(
    "/generate",
    response_model=LLMResponse
)
def generate_llm(
    request: LLMRequest
):

    return llm_service.generate(
        request.prompt,
        request.provider
    )
