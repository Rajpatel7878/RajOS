"""Automation Engine 2.0 — Automation Service.

Handles CRUD operations, enable/disable, manual run, preview,
execution history queries, and the event dispatcher.

All ownership is derived from the authenticated user id passed in by the
router — user-supplied ``user_id`` values are never trusted.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.automation.automation_models import Automation, AutomationRun
from app.automation.automation_schemas import AutomationCreate, AutomationUpdate
from app.automation.condition_engine import condition_engine
from app.automation.trigger_engine import trigger_engine, validate_timezone
from app.automation.execution_engine import (
    execution_engine,
    is_running,
    request_cancel,
    validate_actions,
)

logger = logging.getLogger(__name__)


class AutomationService:

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_definition(
        trigger_type: str,
        trigger_config: Optional[dict],
        conditions: Optional[list],
        actions: Optional[list],
        timezone_name: Optional[str],
    ) -> None:
        """Validate every part of an automation definition.

        Raises ValueError (→ HTTP 422) when the trigger, conditions or actions
        could not be executed safely.  Actions are checked against the Tool
        Registry, so an unknown/disabled/blocked tool is rejected at save time
        rather than silently failing on every future run.
        """
        trigger_engine.validate(trigger_type, trigger_config or {}, timezone_name)
        condition_engine.validate(conditions or [])
        validate_actions(actions or [])

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(
        self,
        db: Session,
        user_id: int,
        data: AutomationCreate,
    ) -> Automation:
        # Validate the trigger definition before persisting anything.
        data.validate_trigger()

        trigger_cfg = (
            data.trigger_config.model_dump(exclude_none=True)
            if data.trigger_config else {}
        )
        conditions = [c.model_dump() for c in (data.conditions or [])]
        actions = [a.model_dump() for a in (data.actions or [])]

        # Re-validate the fully normalised definition (trigger + conditions +
        # actions against the Tool Registry) before anything is persisted.
        self.validate_definition(
            data.trigger_type, trigger_cfg, conditions, actions, data.timezone
        )

        automation = Automation(
            user_id=user_id,
            name=data.name,
            description=data.description,
            # V2 structured
            trigger_type=data.trigger_type,
            trigger_config=trigger_cfg,
            conditions=conditions,
            actions=actions,
            timezone=data.timezone,
            failure_policy=data.failure_policy,
            max_retries=data.max_retries,
            retry_delay_seconds=data.retry_delay_seconds,
            # Legacy compat
            trigger=data.trigger,
            action=data.action,
        )

        # Compute initial next_run_at in the automation's own timezone.
        next_run = trigger_engine.compute_next_run(
            data.trigger_type, trigger_cfg, timezone_name=data.timezone
        )
        automation.next_run_at = next_run

        db.add(automation)
        db.commit()
        db.refresh(automation)

        logger.info(
            "Created automation %d '%s' for user %d (next_run=%s)",
            automation.id, automation.name, user_id,
            next_run.isoformat() if next_run else "N/A"
        )
        return automation

    def get_all(self, db: Session, user_id: int) -> List[Automation]:
        return (
            db.query(Automation)
            .filter(
                Automation.user_id == user_id,
                Automation.archived_at.is_(None),  # noqa: E711
            )
            .order_by(Automation.created_at.desc())
            .all()
        )

    def get_one(
        self,
        db: Session,
        user_id: int,
        automation_id: int,
        include_archived: bool = False,
    ) -> Optional[Automation]:
        query = (
            db.query(Automation)
            .filter(
                Automation.id == automation_id,
                Automation.user_id == user_id,
            )
        )
        if not include_archived:
            query = query.filter(Automation.archived_at.is_(None))  # noqa: E711
        return query.first()

    def update(
        self,
        db: Session,
        automation: Automation,
        data: AutomationUpdate,
    ) -> Automation:
        if data.name is not None:
            automation.name = data.name
        if data.description is not None:
            automation.description = data.description
        if data.enabled is not None:
            automation.enabled = data.enabled
        if data.timezone is not None:
            automation.timezone = validate_timezone(data.timezone)
        if data.failure_policy is not None:
            automation.failure_policy = data.failure_policy
        if data.max_retries is not None:
            automation.max_retries = data.max_retries
        if data.retry_delay_seconds is not None:
            automation.retry_delay_seconds = data.retry_delay_seconds
        if data.trigger_type is not None:
            automation.trigger_type = data.trigger_type
        if data.trigger_config is not None:
            automation.trigger_config = data.trigger_config.model_dump(exclude_none=True)
        if data.conditions is not None:
            automation.conditions = [c.model_dump() for c in data.conditions]
        if data.actions is not None:
            automation.actions = [a.model_dump() for a in data.actions]
        # Legacy compat
        if data.trigger is not None:
            automation.trigger = data.trigger
        if data.action is not None:
            automation.action = data.action

        # Validate the resulting definition, then recompute next_run_at.
        self.validate_definition(
            automation.trigger_type,
            automation.trigger_config or {},
            automation.conditions or [],
            automation.actions or [],
            automation.timezone,
        )
        if data.trigger_type is not None or data.trigger_config is not None \
                or data.timezone is not None:
            automation.next_run_at = trigger_engine.compute_next_run(
                automation.trigger_type,
                automation.trigger_config or {},
                timezone_name=automation.timezone,
            )

        db.commit()
        db.refresh(automation)
        return automation

    def delete(self, db: Session, automation: Automation) -> dict:
        """Archive an automation: removed from the list, never executed again,
        while its execution history is preserved."""
        automation.enabled = False
        automation.archived_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(automation)
        logger.info(
            "Automation %d archived (execution history preserved).", automation.id
        )
        return {
            "message": "Automation deleted. Its execution history was preserved.",
            "id": automation.id,
            "archived": True,
        }

    # ------------------------------------------------------------------
    # Enable / Disable
    # ------------------------------------------------------------------

    def enable(self, db: Session, automation: Automation) -> Automation:
        automation.enabled = True
        # Recompute next_run_at when re-enabling
        automation.next_run_at = trigger_engine.compute_next_run(
            automation.trigger_type,
            automation.trigger_config or {},
            timezone_name=automation.timezone,
        )
        db.commit()
        db.refresh(automation)
        return automation

    def disable(self, db: Session, automation: Automation) -> Automation:
        automation.enabled = False
        db.commit()
        db.refresh(automation)
        return automation

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    def cancel(
        self,
        db: Session,
        automation: Automation,
    ) -> dict:
        """Ask the automation's in-flight run to stop and mark it cancelled.

        The persisted run status is the authoritative signal: the execution
        engine re-reads it before every action, so cancellation also works when
        the API request and the running execution are in different workers.
        """
        if is_running(automation.id):
            request_cancel(automation.id)

        running_runs = (
            db.query(AutomationRun)
            .filter(
                AutomationRun.automation_id == automation.id,
                AutomationRun.user_id == automation.user_id,
                AutomationRun.status == "running",
            )
            .all()
        )
        now = datetime.now(timezone.utc)
        for run in running_runs:
            run.status = "cancelled"
            run.error_message = "Cancelled by user."
            run.completed_at = now
        db.commit()

        logger.info(
            "Cancellation requested for automation %d (%d in-flight run(s)).",
            automation.id, len(running_runs),
        )
        return {
            "automation_id": automation.id,
            "cancelled_runs": len(running_runs),
            "message": (
                "Cancellation requested; the running execution will stop before "
                "its next action."
                if running_runs
                else "No run was in flight — nothing to cancel."
            ),
        }

    # ------------------------------------------------------------------
    # Manual Run
    # ------------------------------------------------------------------

    def run_now(
        self,
        db: Session,
        automation: Automation,
    ) -> AutomationRun:
        """Trigger immediate execution regardless of schedule.

        Goes through exactly the same permission / execution pipeline as the
        scheduler (Run Now is not a privileged path).
        """
        logger.info(
            "Manual run triggered for automation %d by user %d.",
            automation.id, automation.user_id
        )
        return execution_engine.execute(
            automation, db, trigger_source="manual",
            execution_key=f"manual:{uuid4().hex}",
        )

    # ------------------------------------------------------------------
    # Execution History
    # ------------------------------------------------------------------

    def get_runs(
        self,
        db: Session,
        automation_id: int,
        user_id: int,
        limit: int = 50,
    ) -> List[AutomationRun]:
        return (
            db.query(AutomationRun)
            .filter(
                AutomationRun.automation_id == automation_id,
                AutomationRun.user_id == user_id,
            )
            .order_by(AutomationRun.started_at.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def preview(self, automation: Automation) -> dict:
        """Return what would happen on the next run without executing."""
        cfg = automation.trigger_config or {}
        next_run = trigger_engine.compute_next_run(
            automation.trigger_type, cfg, timezone_name=automation.timezone
        )
        return {
            "automation_id": automation.id,
            "next_run_at": next_run.isoformat() if next_run else None,
            "actions": automation.actions or [],
            "conditions": automation.conditions or [],
            "estimated_action_count": len(automation.actions or []),
            "timezone": automation.timezone,
            "enabled": automation.enabled,
            "failure_policy": automation.failure_policy,
        }

    # ------------------------------------------------------------------
    # Event dispatcher (called by other services on state changes)
    # ------------------------------------------------------------------

    def fire_event(
        self,
        db: Session,
        user_id: int,
        event_type: str,
        payload: Optional[dict] = None,
        event_id: Optional[str] = None,
    ) -> List[AutomationRun]:
        """Execute all enabled event-based automations matching event_type.

        ``event_id`` makes delivery idempotent: replaying the same event never
        executes the same automation twice.
        """
        runs: List[AutomationRun] = []
        payload = payload or {}

        automations = (
            db.query(Automation)
            .filter(
                Automation.user_id == user_id,
                Automation.enabled == True,  # noqa: E712
                Automation.archived_at.is_(None),  # noqa: E711
                Automation.trigger_type == "event",
            )
            .all()
        )

        for auto in automations:
            cfg = auto.trigger_config or {}
            if not trigger_engine.matches_event(auto.trigger_type, cfg, event_type):
                continue

            execution_key = (
                f"event:{event_type}:{event_id}" if event_id
                else f"event:{event_type}:{uuid4().hex}"
            )
            logger.info(
                "Event '%s' matched automation %d — executing.", event_type, auto.id
            )
            run = execution_engine.execute(
                auto, db,
                trigger_source=f"event:{event_type}",
                execution_key=execution_key,
            )
            runs.append(run)

        return runs


automation_service = AutomationService()
