from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat_schema import ChatRequest
from app.security.dependencies import get_current_user
from app.services.ai_service import ai_response
from app.conversation.conversation_manager import ConversationManager


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/message")
def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    conversation = Conversation(
        title=request.message[:30],
        user_id=user.id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)


    user_message = Message(
        role="user",
        content=request.message,
        conversation_id=conversation.id
    )

    db.add(user_message)


    conversation_manager = ConversationManager()

    conversation_data = conversation_manager.chat(
        str(user.id),
        request.message
    )

    ai_reply = ai_response(
        request.message
    )

    ai_reply["conversation_context"] = conversation_data


    assistant_message = Message(
        role="assistant",
        content=ai_reply["response"],
        conversation_id=conversation.id
    )

    db.add(assistant_message)

    db.commit()


    return {
        "conversation_id": conversation.id,
        "response": ai_reply["response"]
    }


@router.get("/history")
def chat_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).all()

    result = []

    for conversation in conversations:

        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).all()

        result.append({
            "conversation_id": conversation.id,
            "title": conversation.title,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]
        })

    return result


@router.delete("/history")
def delete_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).all()

    for conversation in conversations:

        db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).delete()

        db.delete(conversation)

    db.commit()

    return {
        "message": "Chat history deleted"
    }
