"""ConversationService for RajOS V2 Phase 3 — Conversation Intelligence 2.0.

Encapsulates all business logic for:
- User-isolated conversation CRUD
- Deterministic message persistence & chronological context history
- Context window management
- Automatic title generation via LLMService
- Manual rename, archive, restore, and search
"""

import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.conversation import Conversation
from app.models.message import Message
from app.llm.llm_service import LLMService

logger = logging.getLogger(__name__)


class ConversationService:
    """Centralized service managing conversation state, persistence, and context."""

    def __init__(self):
        self.llm_service = LLMService()

    def create_conversation(
        self,
        db: Session,
        user_id: int,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation belonging to the given user."""
        initial_title = title.strip() if title else "New Chat"
        conversation = Conversation(
            user_id=user_id,
            title=initial_title[:60],
            user_title=bool(title),
            archived=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """Fetch a specific conversation enforcing strict user ownership."""
        return (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .first()
        )

    def list_conversations(
        self,
        db: Session,
        user_id: int,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """List user conversations ordered by recent activity."""
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        if not include_archived:
            query = query.filter(Conversation.archived == False)  # noqa: E712
        return (
            query.order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def rename_conversation(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
        new_title: str
    ) -> Optional[Conversation]:
        """Manually rename a conversation and lock title against auto-generation."""
        conversation = self.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return None

        clean_title = new_title.strip()[:100]
        if clean_title:
            conversation.title = clean_title
            conversation.user_title = True
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conversation)
        return conversation

    def archive_conversation(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
        archived: bool = True
    ) -> Optional[Conversation]:
        """Archive or restore a conversation."""
        conversation = self.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return None

        conversation.archived = archived
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        return conversation

    def delete_conversation(
        self,
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Safely delete a single conversation and its associated messages."""
        conversation = self.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return False

        db.delete(conversation)
        db.commit()
        return True

    def search_conversations(
        self,
        db: Session,
        user_id: int,
        query_text: str,
        limit: int = 20
    ) -> List[Conversation]:
        """Search user's conversations by title or message content."""
        clean_q = f"%{query_text.strip()}%"
        if not query_text.strip():
            return self.list_conversations(db, user_id, limit=limit)

        return (
            db.query(Conversation)
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.user_id == user_id,
                or_(
                    Conversation.title.ilike(clean_q),
                    Message.content.ilike(clean_q)
                )
            )
            .distinct()
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )

    def save_message(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str
    ) -> Message:
        """Persist a message and update conversation timestamp."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        db.add(message)

        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message

    def get_recent_history(
        self,
        db: Session,
        conversation_id: int,
        limit: int = 20
    ) -> List[Message]:
        """Fetch the last N messages for a conversation in strict chronological order.
        
        Includes both 'user' and 'assistant' roles for complete multi-turn context.
        """
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(messages))

    def auto_generate_title(
        self,
        db: Session,
        conversation_id: int,
        first_message: str
    ) -> Optional[str]:
        """Generate a concise title using LLMService if user hasn't manually renamed it."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation or conversation.user_title:
            return conversation.title if conversation else None

        try:
            prompt = (
                f"Generate a very short, concise topic title (3 to 5 words maximum, no quotes) "
                f"for a conversation starting with this user message: \"{first_message[:200]}\""
            )
            raw_res = self.llm_service.generate(prompt)
            if isinstance(raw_res, dict):
                raw_title = raw_res.get("response", "")
            else:
                raw_title = str(raw_res)

            clean_title = raw_title.strip().strip('"\'`')[:60]
            if clean_title:
                conversation.title = clean_title
                db.commit()
                return clean_title
        except Exception as exc:
            logger.warning("Auto-title generation failed: %s", exc)

        return conversation.title
