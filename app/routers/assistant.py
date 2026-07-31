from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import ai_response


router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):

    return ai_response(
        request.message
    )
