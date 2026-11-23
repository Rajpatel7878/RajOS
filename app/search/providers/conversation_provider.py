"""Conversation and message search provider."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider, contains_any
from app.search.utils.scoring import score_lexical


class ConversationSearchProvider(SearchProvider):
    """Searches conversation titles and message bodies.

    Matches are grouped by conversation so the workspace shows one result per
    conversation, using the best matching message as its snippet.
    """

    resource_type = "conversations"
    display_name = "Conversations"
    default_url = "/chat"

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        candidate_limit = min(limit, self.candidate_limit)
        hits: Dict[int, ProviderHit] = {}

        title_condition = contains_any([Conversation.title], query.terms)
        title_query = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.title.isnot(None),
        )
        if title_condition is not None:
            title_query = title_query.filter(title_condition)
        if query.date_from is not None:
            title_query = title_query.filter(Conversation.updated_at >= query.date_from)
        if query.date_to is not None:
            title_query = title_query.filter(Conversation.updated_at <= query.date_to)

        for conversation in title_query.order_by(Conversation.updated_at.desc()).limit(candidate_limit).all():
            hit = self.make_hit(
                resource_id=conversation.id,
                title=conversation.title,
                snippet_source=conversation.title,
                query=query,
                fields={"title": conversation.title},
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                metadata={"archived": bool(conversation.archived)},
            )
            if hit.matched_fields:
                hits[conversation.id] = hit

        message_condition = contains_any([Message.content], query.terms)
        if message_condition is not None:
            message_query = (
                db.query(Message, Conversation)
                .join(Conversation, Message.conversation_id == Conversation.id)
                .filter(Conversation.user_id == user_id, message_condition)
            )
            if query.date_from is not None:
                message_query = message_query.filter(Message.created_at >= query.date_from)
            if query.date_to is not None:
                message_query = message_query.filter(Message.created_at <= query.date_to)

            messages = (
                message_query.order_by(Message.created_at.desc())
                .limit(candidate_limit * 2)
                .all()
            )

            for message, conversation in messages:
                score = score_lexical(conversation.title, [message.content], query.text)
                existing = hits.get(conversation.id)
                if existing is not None and existing.lexical_score >= score.combined:
                    continue

                hit = self.make_hit(
                    resource_id=conversation.id,
                    title=conversation.title or "Untitled conversation",
                    snippet_source=message.content,
                    query=query,
                    fields={
                        "title": conversation.title,
                        "message": message.content,
                    },
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at,
                    metadata={
                        "archived": bool(conversation.archived),
                        "message_role": message.role,
                    },
                )
                if hit.matched_fields:
                    hits[conversation.id] = hit

        return list(hits.values())

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        condition = contains_any([Conversation.title], terms)
        if condition is None:
            return []
        rows = (
            db.query(Conversation.id, Conversation.title)
            .filter(
                Conversation.user_id == user_id,
                Conversation.title.isnot(None),
                condition,
            )
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "text": row.title,
                "kind": "resource",
                "resource_type": self.resource_type,
                "resource_id": str(row.id),
                "url": self.default_url,
            }
            for row in rows
        ]
