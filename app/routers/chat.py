from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat_schema import ChatRequest
from app.security.dependencies import get_current_user
from app.services.ai_service import ai_response
from app.services.profile_manager import ProfileManager
from app.services.profile_query import ProfileQuery
from app.services.preference_extractor import PreferenceExtractor
from app.services.preference_manager import PreferenceManager
from app.services.preference_query import PreferenceQuery
from app.services.context_builder import ContextBuilder
from app.conversation.conversation_manager import ConversationManager
from app.memory.memory_engine import MemoryEngine


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

    conversation = None

    if request.conversation_id:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user.id
            )
            .first()
        )

    if conversation is None:

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
    memory_engine = MemoryEngine()
    profile_manager = ProfileManager()
    context_builder = ContextBuilder()

    profile_manager.process(
        db,
        user.id,
        request.message
    )

    profile_query = ProfileQuery()
    preference_extractor = PreferenceExtractor()
    preference_manager = PreferenceManager()
    preference_query = PreferenceQuery()

    profile_name = None

    if 'name' in request.message.lower():

        profile_name = profile_query.get_profile(
            db,
            user.id,
            'name'
        )

    preference = preference_extractor.extract(request.message)

    if preference:
        key, value = preference
        preference_manager.save_preference(
            db,
            user.id,
            key,
            value
        )

    history = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).all()

    history_text = [
        msg.content
        for msg in history
        if msg.role == "user"
    ]

    conversation_data = conversation_manager.chat(
        str(user.id),
        request.message,
        history_text
    )

    full_context = context_builder.build(
        db,
        user.id,
        memory_data=[],
        conversation_history=history_text
    )

    if profile_name:
        memory_data = []
    else:
        memory_data = memory_engine.process_memory(
            request.message
        )

    if profile_name:

        ai_reply = {
            "response": f"Your name is {profile_name}.",
            "memory": [],
            "conversation_context": conversation_data,
            "agent": {}
        }

    else:

        ai_reply = ai_response(
            request.message,
            user,
            full_context
        )

    ai_reply["memory"] = memory_data

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
        "response": ai_reply["response"],
        "memory": ai_reply["memory"],
        "conversation_context": ai_reply["conversation_context"],
        "agent": ai_reply["agent"]
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
