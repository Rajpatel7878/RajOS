"""Default provider registry for RajOS unified search."""

from __future__ import annotations

from typing import List

from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider
from app.search.providers.conversation_provider import ConversationSearchProvider
from app.search.providers.document_provider import DocumentSearchProvider
from app.search.providers.knowledge_provider import KnowledgeSearchProvider
from app.search.providers.memory_provider import MemorySearchProvider
from app.search.providers.note_provider import NoteSearchProvider
from app.search.providers.task_provider import TaskSearchProvider

__all__ = [
    "ProviderHit",
    "ProviderQuery",
    "SearchProvider",
    "DEFAULT_PROVIDER_CLASSES",
    "default_providers",
    "SUPPORTED_RESOURCE_TYPES",
]

DEFAULT_PROVIDER_CLASSES = (
    TaskSearchProvider,
    NoteSearchProvider,
    DocumentSearchProvider,
    ConversationSearchProvider,
    MemorySearchProvider,
    KnowledgeSearchProvider,
)

SUPPORTED_RESOURCE_TYPES = tuple(cls.resource_type for cls in DEFAULT_PROVIDER_CLASSES)


def default_providers() -> List[SearchProvider]:
    """Instantiate a fresh set of providers (providers are stateless)."""
    return [provider_class() for provider_class in DEFAULT_PROVIDER_CLASSES]
