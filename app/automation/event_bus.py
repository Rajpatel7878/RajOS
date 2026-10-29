"""Automation Engine 2.0 — Lightweight Event Bus.

A thin, fail-safe wrapper around the automation event dispatcher.  Domain code
(tasks, notes, agents …) calls ``emit(...)`` when something meaningful happens;
matching event-based automations are executed through the normal
Automation → Permission → Tool Registry pipeline.

Rules:
  * Events never break the business flow that produced them (best effort).
  * Event payloads are owned by the emitting user — never trusted for identity.
  * ``event_id`` makes delivery idempotent (replayed events do not re-run).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def emit(
    db,
    user_id: int,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None,
) -> List[Any]:
    """Dispatch an event to matching event-based automations (synchronously).

    Returns the created AutomationRun records.  Failures are logged and
    swallowed: an automation problem must never break a task/note operation.
    """
    try:
        from app.automation.automation_service import automation_service

        return automation_service.fire_event(
            db,
            user_id=user_id,
            event_type=event_type,
            payload=payload,
            event_id=event_id,
        )
    except Exception as exc:
        logger.warning(
            "Event '%s' dispatch failed (user %s): %s", event_type, user_id, exc
        )
        return []
