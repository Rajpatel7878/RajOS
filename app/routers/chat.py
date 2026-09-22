from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ConversationRead,
    ConversationDetail,
    ConversationRename,
    ConversationArchive,
)
from app.security.dependencies import get_current_user
from app.services.ai_service import ai_response
from app.services.profile_manager import ProfileManager
from app.services.profile_query import ProfileQuery
from app.services.preference_extractor import PreferenceExtractor
from app.services.preference_manager import PreferenceManager
from app.services.context_builder import ContextBuilder
from app.services.conversation_service import ConversationService
from app.conversation.conversation_manager import ConversationManager
from app.memory.memory_engine import MemoryEngine
from app.memory.memory_service import memory_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

conversation_service = ConversationService()


@router.post("/message", response_model=ChatResponse)
def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Send a chat message, build multi-turn context, and return AI reply."""

    # 1. Resolve or create conversation
    conversation = None
    if request.conversation_id:
        conversation = conversation_service.get_conversation(db, request.conversation_id, user.id)

    if conversation is None:
        conversation = conversation_service.create_conversation(db, user.id, title=None)

    # 2. Persist user message
    user_message = conversation_service.save_message(
        db,
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    # 3. Auxiliary processing (Profile & Preferences)
    profile_manager = ProfileManager()
    profile_manager.process(db, user.id, request.message)

    profile_name = None
    if "name" in request.message.lower():
        profile_query = ProfileQuery()
        profile_name = profile_query.get_profile(db, user.id, "name")

    preference_extractor = PreferenceExtractor()
    preference = preference_extractor.extract(request.message)
    if preference:
        key, val = preference
        preference_manager = PreferenceManager()
        preference_manager.save_preference(db, user.id, key, val)

    # 4. Context building with multi-turn history (user + assistant) capped at recent 20 messages
    recent_messages = conversation_service.get_recent_history(db, conversation.id, limit=20)
    history_payload = [
        {"role": msg.role, "content": msg.content}
        for msg in recent_messages
    ]

    context_builder = ContextBuilder()
    full_context = context_builder.build(
        db,
        user.id,
        query_text=request.message,
        memory_data=[],
        conversation_history=history_payload
    )

    # 4b. Failure-isolated Memory 2.0 processing (explicit intent parsing & candidate extraction)
    memory_data = []
    try:
        handled, msg, mem_obj = memory_service.parse_and_handle_explicit_intent(
            db=db,
            user_id=user.id,
            user_message=request.message
        )
        if handled and mem_obj:
            memory_data.append({"key": mem_obj.key, "value": mem_obj.value, "status": "explicit_handled"})
        else:
            extracted = memory_service.extract_memories_from_conversation(
                db=db,
                user_id=user.id,
                user_message=request.message
            )
            for item in extracted:
                mem_item = item.get("memory")
                if mem_item:
                    memory_data.append({"key": mem_item.key, "value": mem_item.value, "status": item.get("status")})
    except Exception as e:
        print(f"[ChatRouter] Failure processing Memory 2.0 (isolated): {e}")

    # 5. Generate AI response via Phase 2 LLM Core
    conversation_manager = ConversationManager()
    conversation_data = conversation_manager.chat(
        str(user.id),
        request.message,
        [m["content"] for m in history_payload if m["role"] == "user"]
    )

    if profile_name:
        ai_reply = {
            "response": f"Your name is {profile_name}.",
            "memory": [],
            "conversation_context": conversation_data,
            "agent": {}
        }
    else:
        ai_reply = ai_response(request.message, user, full_context)

    ai_reply["memory"] = memory_data
    ai_reply["conversation_context"] = conversation_data

    # 6. Persist assistant message
    conversation_service.save_message(
        db,
        conversation_id=conversation.id,
        role="assistant",
        content=ai_reply["response"]
    )

    # 7. Auto-generate title on initial interaction if title is not locked
    if not conversation.user_title and len(recent_messages) <= 2:
        conversation_service.auto_generate_title(db, conversation.id, request.message)

    return {
        "conversation_id": conversation.id,
        "response": ai_reply["response"],
        "memory": ai_reply.get("memory", []),
        "conversation_context": ai_reply.get("conversation_context"),
        "agent": ai_reply.get("agent"),
        "sources": full_context.get("rag_sources", [])
    }


# ------------------------------------------------------------------
# Conversation Management REST Endpoints
# ------------------------------------------------------------------

@router.get("/conversations", response_model=List[ConversationRead])
def list_conversations(
    include_archived: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List authenticated user's conversations ordered by recent activity."""
    return conversation_service.list_conversations(
        db,
        user.id,
        include_archived=include_archived,
        limit=limit,
        offset=offset
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Fetch single conversation metadata and ordered messages with user ownership check."""
    conversation = conversation_service.get_conversation(db, conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationRead)
def rename_conversation(
    conversation_id: int,
    payload: ConversationRename,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Manually rename a conversation title."""
    conversation = conversation_service.rename_conversation(
        db,
        conversation_id,
        user.id,
        payload.title
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/conversations/{conversation_id}/archive", response_model=ConversationRead)
def archive_conversation(
    conversation_id: int,
    payload: ConversationArchive,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Archive or restore a conversation."""
    conversation = conversation_service.archive_conversation(
        db,
        conversation_id,
        user.id,
        archived=payload.archived
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_single_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a single conversation and its message history."""
    deleted = conversation_service.delete_conversation(db, conversation_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully", "id": conversation_id}


@router.get("/search", response_model=List[ConversationRead])
def search_conversations(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Search user's conversations by title or message content."""
    return conversation_service.search_conversations(db, user.id, q, limit=limit)


# ------------------------------------------------------------------
# Backward-Compatibility Endpoints
# ------------------------------------------------------------------

@router.get("/history")
def chat_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Legacy endpoint returning nested list of conversations and messages."""
    conversations = conversation_service.list_conversations(db, user.id, include_archived=True)
    result = []
    for conv in conversations:
        result.append({
            "conversation_id": conv.id,
            "title": conv.title,
            "archived": conv.archived,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in conv.messages
            ]
        })
    return result


@router.delete("/history")
def delete_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Legacy endpoint clearing all conversations for the authenticated user."""
    conversations = conversation_service.list_conversations(db, user.id, include_archived=True)
    for conv in conversations:
        conversation_service.delete_conversation(db, conv.id, user.id)
    return {"message": "Chat history deleted"}
