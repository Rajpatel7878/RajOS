"""Automation Engine 2.0 — Background Scheduler.

A single centralized async polling loop (never one loop per automation) that:

  1. Loads enabled automations whose persisted ``next_run_at`` is due
  2. Delegates execution to the Automation ExecutionEngine
  3. Recomputes and stores ``next_run_at`` after every attempt
  4. Handles schedule / interval / one-time / condition / deadline triggers
  5. Survives restarts — all schedule state lives in the database, and runs
     are deduplicated by (automation_id, execution_key)

Start with: scheduler.start()   (called from main.py startup hook)
Stop  with: scheduler.stop()
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Polling interval in seconds — check for due automations every 60 s
_POLL_INTERVAL = 60

# Safety valve: never start more than this many runs in a single tick.
_MAX_RUNS_PER_TICK = 25


class AutomationScheduler:

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._recovered = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler loop (idempotent)."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop(), name="automation-scheduler")
        logger.info("Automation scheduler started (poll every %ds).", _POLL_INTERVAL)

    def stop(self) -> None:
        """Gracefully stop the scheduler."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Automation scheduler stopped.")

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    async def _loop(self) -> None:
        while self._running:
            try:
                await self._tick()
            except Exception as exc:
                logger.exception("Scheduler tick error: %s", exc)
            await asyncio.sleep(_POLL_INTERVAL)

    async def _tick(self) -> None:
        """Find and execute all due automations (each in its own thread/session)."""
        from app.database.connection import SessionLocal
        from app.automation.automation_models import Automation
        from app.automation.trigger_engine import SCHEDULER_TRIGGER_TYPES

        if not self._recovered:
            self._recover_interrupted_runs()
            self._recovered = True

        now = datetime.now(timezone.utc)
        due: List[Tuple[int, str, str]] = []

        db = SessionLocal()
        try:
            rows = (
                db.query(Automation.id, Automation.next_run_at, Automation.trigger_type)
                .filter(
                    Automation.enabled == True,  # noqa: E712
                    Automation.archived_at.is_(None),  # noqa: E711
                    Automation.trigger_type.in_(list(SCHEDULER_TRIGGER_TYPES)),
                    Automation.next_run_at.isnot(None),
                    Automation.next_run_at <= now,
                )
                .limit(_MAX_RUNS_PER_TICK)
                .all()
            )
            due = [(r.id, r.next_run_at.isoformat(), r.trigger_type) for r in rows]
        finally:
            db.close()

        if due:
            logger.info("Scheduler tick: %d automation(s) due.", len(due))

        for automation_id, slot_iso, trigger_type in due:
            if not self._running:
                break
            try:
                # Each run gets its own thread + database session.
                await asyncio.to_thread(
                    self._run_one, automation_id, slot_iso, trigger_type
                )
            except Exception as exc:
                logger.exception(
                    "Failed to execute automation %d: %s", automation_id, exc
                )

    # ------------------------------------------------------------------
    # Single due automation
    # ------------------------------------------------------------------

    def _run_one(
        self,
        automation_id: int,
        slot_iso: str,
        trigger_type: str,
    ) -> None:
        """Execute one due automation in a dedicated session, then advance it."""
        from app.database.connection import SessionLocal
        from app.automation.automation_models import Automation
        from app.automation.trigger_engine import trigger_engine
        from app.automation.condition_engine import condition_engine
        from app.automation.execution_engine import execution_engine

        db = SessionLocal()
        try:
            automation = db.query(Automation).filter(
                Automation.id == automation_id
            ).first()
            if not automation or not automation.enabled:
                return

            slot = datetime.fromisoformat(slot_iso)
            if automation.next_run_at is None or (
                automation.next_run_at.isoformat() != slot_iso
                and abs(
                    (automation.next_run_at - slot).total_seconds()
                ) > 1
            ):
                # Another worker already advanced this automation.
                logger.info(
                    "Automation %d slot changed (%s → %s) — skipping stale claim.",
                    automation_id, slot_iso,
                    automation.next_run_at.isoformat() if automation.next_run_at else "None",
                )
                return

            cfg = automation.trigger_config or {}

            if trigger_type == "deadline":
                self._run_deadline(db, automation, cfg, slot)
            elif trigger_type == "condition":
                # Only record a run when the guard conditions actually hold.
                if condition_engine.evaluate(
                    automation.conditions or [], db, automation.user_id
                ):
                    execution_engine.execute(
                        automation,
                        db,
                        trigger_source="scheduler",
                        execution_key=f"condition:{slot_iso}",
                    )
                else:
                    logger.info(
                        "Automation %d condition poll: not satisfied — no run recorded.",
                        automation_id,
                    )
            else:
                execution_engine.execute(
                    automation,
                    db,
                    trigger_source="scheduler",
                    execution_key=f"schedule:{slot_iso}",
                )

            # Advance the schedule (always, so a failure can't hot-loop).
            next_run = trigger_engine.compute_next_run(
                automation.trigger_type,
                cfg,
                after=datetime.now(timezone.utc),
                timezone_name=automation.timezone,
            )
            automation.next_run_at = next_run

            # One-time automations: disable after firing
            if automation.trigger_type == "onetime":
                automation.enabled = False

            db.commit()
            logger.info(
                "Automation %d next_run_at → %s",
                automation_id,
                next_run.isoformat() if next_run else "None (disabled)",
            )
        finally:
            db.close()

    def _run_deadline(
        self,
        db,
        automation,
        cfg: dict,
        slot: datetime,
    ) -> None:
        """Fire a deadline automation for every task entering the reminder window."""
        from app.automation.execution_engine import execution_engine
        from app.models.task import Task

        hours = float(cfg.get("deadline_hours", 24))
        # Task.due_date is stored as naive UTC across RajOS (see the Phase 8
        # productivity services), so compare using the same convention.
        now = datetime.utcnow()
        horizon = now + timedelta(hours=hours)

        tasks = (
            db.query(Task)
            .filter(
                Task.user_id == automation.user_id,
                Task.completed == False,  # noqa: E712
                Task.due_date.isnot(None),
                Task.due_date <= horizon,
                Task.due_date > now,
            )
            .all()
        )

        for task in tasks:
            due_iso = task.due_date.isoformat()
            execution_engine.execute(
                automation,
                db,
                trigger_source=f"deadline:task:{task.id}",
                execution_key=f"deadline:{task.id}:{due_iso}",
            )

    # ------------------------------------------------------------------
    # Restart recovery
    # ------------------------------------------------------------------

    @staticmethod
    def _recover_interrupted_runs() -> None:
        """Mark runs left in 'running' by a crash/restart as failed."""
        from app.database.connection import SessionLocal
        from app.automation.automation_models import AutomationRun

        db = SessionLocal()
        try:
            stuck = (
                db.query(AutomationRun)
                .filter(AutomationRun.status == "running")
                .all()
            )
            if not stuck:
                return
            now = datetime.now(timezone.utc)
            for run in stuck:
                run.status = "failed"
                run.error_message = "Interrupted by server restart."
                run.completed_at = now
            db.commit()
            logger.warning(
                "Recovered %d interrupted automation run(s) after restart.",
                len(stuck),
            )
        except Exception as exc:  # recovery must never block the scheduler
            db.rollback()
            logger.exception("Run recovery failed: %s", exc)
        finally:
            db.close()


# Singleton
scheduler = AutomationScheduler()
