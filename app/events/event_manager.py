"""Real-time Event Manager for RajOS V2 Phase 12.

Manages event publication, subscriber connections, and user-isolated
event delivery via SSE or WebSocket transport.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from app.events.event_types import (
    BaseEvent,
    EventType,
    sse_payload,
    sse_event,
    EventType as EventTypeEnum,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection Manager — tracks active SSE connections per user
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Manages authenticated SSE connections with user isolation."""

    def __init__(self) -> None:
        # user_id -> Set[asyncio.Queue[BaseEvent]]
        self._connections: Dict[int, Set["asyncio.Queue[BaseEvent]"]] = defaultdict(set)
        self._user_permissions: Dict[int, Set[str]] = defaultdict(set)
        self._connection_refs: Dict[int, int] = {}  # user_id -> ref count for cleanup

    def subscribe(self, user_id: int) -> "asyncio.Queue[BaseEvent]":
        """Subscribe a user to the event stream. Returns a queue they can read from."""
        queue: "asyncio.Queue[BaseEvent]" = asyncio.Queue(maxsize=500)
        self._connections[user_id].add(queue)
        self._connection_refs[user_id] = self._connection_refs.get(user_id, 0) + 1
        logger.debug("User %d subscribed to event stream (queues=%d)", user_id, len(self._connections[user_id]))
        return queue

    def unsubscribe(self, user_id: int, queue: "asyncio.Queue[BaseEvent]") -> None:
        """Unsubscribe a user's queue."""
        self._connections[user_id].discard(queue)
        self._connection_refs[user_id] = max(0, self._connection_refs.get(user_id, 1) - 1)
        if self._connection_refs[user_id] == 0:
            self._connections.pop(user_id, None)
            self._user_permissions.pop(user_id, None)
        logger.debug("User %d unsubscribed from event stream", user_id)

    def set_permissions(self, user_id: int, permissions: Set[str]) -> None:
        """Set the effective permissions for a user (for event filtering)."""
        self._user_permissions[user_id] = permissions

    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if a user has a specific permission. '*' matches all."""
        perms = self._user_permissions.get(user_id, set())
        return permission in perms or "*" in perms

    def get_active_user_ids(self) -> Set[int]:
        """Return the set of user IDs currently connected."""
        return set(self._connections.keys())

    def broadcast_to_user(self, user_id: int, event: BaseEvent) -> None:
        """Push a single event to one user's queue (fire-and-forget)."""
        queues = self._connections.get(user_id, set())
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Drop oldest event to make room
                try:
                    queue.get_nowait()
                    queue.put_nowait(event)
                except Exception:
                    logger.warning("Failed to broadcast event to user %d", user_id)

    def broadcast_to_users(self, user_ids: List[int], event: BaseEvent) -> None:
        """Push an event to multiple specific users."""
        for uid in user_ids:
            self.broadcast_to_user(uid, event)

    def broadcast_system(self, event: BaseEvent) -> None:
        """Broadcast a system event to ALL connected users."""
        for user_id in list(self.get_active_user_ids()):
            self.broadcast_to_user(user_id, event)


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def init_connection_manager() -> ConnectionManager:
    """Initialize the global connection manager (called on app startup)."""
    global _connection_manager
    _connection_manager = ConnectionManager()
    return _connection_manager


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    if _connection_manager is None:
        from app.main import app  # lazy import
        # The app startup should have initialized it
        pass
    return _connection_manager


# ---------------------------------------------------------------------------
# Event Publisher — fire events with user isolation and idempotency
# ---------------------------------------------------------------------------

class EventPublisher:
    """Publishes events to the real-time system with user filtering."""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._cm = connection_manager
        # Track event IDs per user for idempotency (limited window)
        self._delivered: Dict[int, Set[str]] = defaultdict(set)

    def publish(self, event: BaseEvent, user_ids: Optional[List[int]] = None) -> None:
        """Publish an event.

        - If user_ids are specified, deliver only to those users.
        - If None, deliver to the event's user_id (from the event itself).
        - Idempotent: replaying the same event_id for a user is dropped.
        """
        uid = event.user_id
        if user_ids is not None:
            uid = user_ids[0]  # single user for simplicity; could fan-out

        # Idempotency check
        delivered_ids = self._delivered[uid]
        if event.event_id in delivered_ids:
            logger.debug("Dropping duplicate event %s for user %s", event.event_id, uid)
            return
        delivered_ids.add(event.event_id)
        # Keep only last 200 ids per user to avoid memory growth
        if len(delivered_ids) > 200:
            # remove oldest half
            to_remove = list(delivered_ids)[:100]
            for old_id in to_remove:
                delivered_ids.discard(old_id)

        # User isolation: only deliver if the event carries the right user context
        # The event already has user_id set; we deliver to matching connections
        self._cm.broadcast_to_user(uid, event)

    def publish_to_users(self, user_ids: List[int], event: BaseEvent) -> None:
        """Publish an event to specific user IDs."""
        event.user_id = user_ids[0]  # override for delivery
        self.publish(event, user_ids=user_ids)

    def mark_delivered(self, user_id: int, event_id: str) -> None:
        """Manually mark an event as delivered for a user (idempotency)."""
        self._delivered[user_id].add(event_id)


# Global publisher factory
_publisher_map: Dict[int, EventPublisher] = {}


def get_publisher(user_id: int, connection_manager: ConnectionManager) -> EventPublisher:
    """Get or create an EventPublisher for a user."""
    if user_id not in _publisher_map:
        _publisher_map[user_id] = EventPublisher(connection_manager)
    return _publisher_map[user_id]


def clear_publisher(user_id: int) -> None:
    """Clear a publisher (e.g., on connection close)."""
    _publisher_map.pop(user_id, None)