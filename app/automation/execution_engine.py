"""Automation Engine 2.0 — Execution Engine.

Executes an Automation's action list sequentially through the Phase 6
Tool Registry.  Enforces, on every single run:

  - Owner re-check (user still exists; automation still belongs to them)
  - Automation enabled check
  - Condition guard (delegated to ConditionEngine)
  - Tool allow-list / tool exists / tool enabled
  - Argument sanitisation (ownership always derived from the owner user)
  - Confirmation policy (dangerous tools are never silently bypassed)
  - Controlled retries for transient failures only
  - Failure policy (stop | continue)
  - Idempotency via a unique (automation_id, execution_key) pair
  - Recursion / loop protection (depth cap + re-entrancy guard)
  - Notification of completed / partial / failed runs
  - Full execution log stored in AutomationRun

The scheduler never executes actions itself — it only calls
``execution_engine.execute(...)``.
"""

from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.automation.automation_models import Automation, AutomationRun
from app.automation.condition_engine import condition_engine
from app.tools.tool_executor import tool_executor
from app.tools.tool_context import ToolExecutionContext

logger = logging.getLogger(__name__)

# Maximum nesting depth to prevent automation → tool → event → automation loops
_MAX_DEPTH = 3

# Recursion depth of the currently executing stack (context-local, thread-safe).
_EXECUTION_DEPTH: ContextVar[int] = ContextVar("automation_execution_depth", default=0)

# Automations currently executing in this process — blocks re-entrancy/loops.
_ACTIVE_RUNS: set[str] = set()

# Automations whose current in-flight run the user asked to cancel (process-local
# fast path; the persisted run status is the authoritative cross-process signal).
_CANCEL_REQUESTED: set[int] = set()

# Burst guard: an automation may not start more than this many runs inside
# _RATE_WINDOW_SECONDS.  Protects against automation storms (e.g. a task loop
# emitting hundreds of identical events) without restricting normal use.
_MAX_RUNS_PER_WINDOW = 30
_RATE_WINDOW_SECONDS = 60.0
_RUN_TIMESTAMPS: Dict[int, List[float]] = {}

# Tools that must never be reachable from an automation, even if someone
# registers them later.  Defence in depth on top of the Tool Registry.
AUTOMATION_BLOCKED_TOOLS = frozenset({
    "run_shell", "execute_shell", "bash", "execute_sql", "run_sql",
    "execute_python", "run_python", "eval", "exec",
    "read_file", "write_file", "delete_file", "filesystem",
    "http_request", "network_request", "webhook",
})

# Ownership fields that must never come from stored action arguments.
_UNSAFE_ARGUMENT_KEYS = {"user_id", "owner_id", "owner", "conversation_id"}

# Only genuinely transient errors are retried (never permission, validation,
# missing tool, confirmation or cancellation failures).
_RETRYABLE_ERRORS = {"EXECUTION_FAILED", "TIMEOUT", "RATE_LIMITED"}


def current_depth() -> int:
    """Recursion depth of the current execution stack."""
    return _EXECUTION_DEPTH.get()


def validate_actions(actions: List[Dict[str, Any]]) -> None:
    """Validate an action list before it is ever persisted.

    Mirrors the execution engine's pre-flight checks so a user cannot save an
    automation whose actions could never run (unknown tool, disabled tool,
    blocked tool, or a dangerous tool without explicit pre-approval).

    Raises ValueError with a user-facing message on the first problem found.
    """
    for index, action in enumerate(actions or [], start=1):
        if not isinstance(action, dict):
            raise ValueError(f"Action {index} must be an object.")
        problem = ExecutionEngine._pre_flight(
            str(action.get("tool_name") or ""), action
        )
        if problem:
            raise ValueError(f"Action {index}: {problem}")


def is_running(automation_id: int) -> bool:
    """True when this automation currently has an execution in this process."""
    return str(automation_id) in _ACTIVE_RUNS


def request_cancel(automation_id: int) -> None:
    """Ask the in-flight run of this automation (if any) to stop."""
    _CANCEL_REQUESTED.add(int(automation_id))


def _rate_limited(automation_id: int) -> bool:
    """Return True when this automation has exceeded its burst allowance."""
    now = time.monotonic()
    window = [t for t in _RUN_TIMESTAMPS.get(automation_id, []) if now - t < _RATE_WINDOW_SECONDS]
    if len(window) >= _MAX_RUNS_PER_WINDOW:
        _RUN_TIMESTAMPS[automation_id] = window
        return True
    window.append(now)
    _RUN_TIMESTAMPS[automation_id] = window
    return False


class ExecutionEngine:
    """Orchestrates full automation execution through the Tool Registry."""

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def execute(
        self,
        automation: Automation,
        db: Session,
        trigger_source: str = "scheduler",
        depth: Optional[int] = None,
        execution_key: Optional[str] = None,
        notify: bool = True,
    ) -> AutomationRun:
        """Execute an automation and return the resulting AutomationRun record.

        Args:
            automation:      The Automation ORM object.
            db:              Active database session.
            trigger_source:  What caused this run ("scheduler"|"event:X"|"manual"|...).
            depth:           Recursion depth; defaults to the ambient depth so
                             nested executions (event chains) are counted.
            execution_key:   Idempotency key for this logical trigger.  When two
                             workers observe the same trigger, only one run is
                             persisted/executed.
            notify:          Whether to notify the owner about the outcome.
        """
        run_id = str(uuid.uuid4())
        depth = current_depth() if depth is None else depth

        # --- Guard: recursion depth (recorded, but never executed) ---
        if depth >= _MAX_DEPTH:
            logger.error(
                "Automation %d blocked: max recursion depth %d reached.",
                automation.id, _MAX_DEPTH,
            )
            return self._persist_run(
                db, run_id, automation, trigger_source,
                status="skipped",
                error_message=f"Blocked: max recursion depth {_MAX_DEPTH} reached.",
                log=[],
            )

        # --- Guard: loop / re-entrancy ---
        if str(automation.id) in _ACTIVE_RUNS:
            logger.error("Automation %d blocked: execution loop detected.", automation.id)
            return self._persist_run(
                db, run_id, automation, trigger_source,
                status="skipped",
                error_message="Blocked: execution loop detected.",
                log=[],
            )

        # --- Guard: owner still exists + automation still enabled ---
        user = db.get(_user_model(), automation.user_id)
        if user is None:
            return self._persist_run(
                db, run_id, automation, trigger_source,
                status="skipped",
                error_message="Owner no longer exists.",
                log=[],
            )
        if not automation.enabled:
            return self._persist_run(
                db, run_id, automation, trigger_source,
                status="skipped",
                error_message="Automation is disabled.",
                log=[],
            )

        # --- Burst guard: refuse an automation storm (recorded as skipped) ---
        if _rate_limited(automation.id):
            logger.warning(
                "Automation %d rate limited (>%d runs in %ds).",
                automation.id, _MAX_RUNS_PER_WINDOW, int(_RATE_WINDOW_SECONDS),
            )
            return self._persist_run(
                db, run_id, automation, trigger_source,
                status="skipped",
                error_message=(
                    f"Rate limited: more than {_MAX_RUNS_PER_WINDOW} runs "
                    f"within {int(_RATE_WINDOW_SECONDS)}s."
                ),
                log=[],
            )

        # --- Idempotency: reserve this logical trigger before doing anything ---
        run = self._reserve_run(
            db, run_id, automation, trigger_source, execution_key
        )
        if run is None:
            # Another worker already claimed this execution key.
            existing = (
                db.query(AutomationRun)
                .filter(
                    AutomationRun.automation_id == automation.id,
                    AutomationRun.execution_key == execution_key,
                )
                .first()
            )
            logger.info(
                "Automation %d duplicate trigger '%s' skipped (run %s exists).",
                automation.id, execution_key,
                existing.id if existing else "?",
            )
            if existing is not None:
                return existing
            return self._persist_run(
                db, run_id, automation, trigger_source,                    status="skipped",
                    error_message="Duplicate trigger ignored.",
                    log=[],
                )

        # Any cancel flag left over from a previous run must not affect this one.
        _CANCEL_REQUESTED.discard(automation.id)

        # --- Enter execution scope (recursion tracking) ---
        depth_token = _EXECUTION_DEPTH.set(depth + 1)
        _ACTIVE_RUNS.add(str(automation.id))
        execution_log: List[Dict[str, Any]] = []

        try:
            # --- Guard: condition check ---
            conditions = automation.conditions or []
            if conditions and not condition_engine.evaluate(
                conditions, db, automation.user_id
            ):
                logger.info("Automation %d skipped: conditions not met.", automation.id)
                return self._finish_run(
                    db, run, automation,
                    status="skipped",
                    error_message="Conditions not satisfied.",
                    log=[],
                )

            # --- Actions ---
            actions = automation.actions or []
            if not actions and automation.action:
                actions = [{"tool_name": automation.action, "arguments": {}}]

            if not actions:
                return self._finish_run(
                    db, run, automation,
                    status="completed",
                    error_message="No actions defined.",
                    log=[],
                )

            context = ToolExecutionContext(
                user_id=automation.user_id,
                conversation_id=None,
                request_id=run_id,
                permissions=["*"],  # the owner's own permissions, re-checked per tool
                metadata={
                    "source": "automation",
                    "automation_id": automation.id,
                    "trigger_source": trigger_source,
                    "execution_key": execution_key,
                },
            )

            failed_count = 0
            max_retries = int(automation.max_retries or 0)
            retry_delay = float(automation.retry_delay_seconds or 0.0)

            for idx, action in enumerate(actions):
                if self._is_cancelled(automation, db, run):
                    logger.info(
                        "Automation %d cancelled by user before action %d/%d.",
                        automation.id, idx + 1, len(actions),
                    )
                    cancelled = self._finish_run(
                        db, run, automation,
                        status="cancelled",
                        error_message="Cancelled by user.",
                        log=execution_log,
                        actions_attempted=len(execution_log),
                        actions_completed=sum(
                            1 for s in execution_log if s.get("status") == "success"
                        ),
                    )
                    if notify:
                        self._notify(db, automation, cancelled)
                    return cancelled

                step_log = self._run_action(
                    automation=automation,
                    action=action,
                    step=idx + 1,
                    total=len(actions),
                    context=context,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )
                execution_log.append(step_log)

                if step_log.get("status") != "success":
                    failed_count += 1
                    if automation.failure_policy != "continue":
                        # stop_on_failure: remaining actions are not attempted.
                        break

            attempted = len(execution_log)
            completed = sum(1 for s in execution_log if s.get("status") == "success")
            overall_status = (
                "completed" if failed_count == 0
                else "partial" if completed > 0
                else "failed"
            )
            error_message = (
                None if failed_count == 0 else f"{failed_count} action(s) failed."
            )

            finished = self._finish_run(
                db, run, automation,
                status=overall_status,
                error_message=error_message,
                log=execution_log,
                actions_attempted=attempted,
                actions_completed=completed,
            )
            if notify:
                self._notify(db, automation, finished)
            return finished

        finally:
            _ACTIVE_RUNS.discard(str(automation.id))
            _CANCEL_REQUESTED.discard(automation.id)
            _EXECUTION_DEPTH.reset(depth_token)

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    @staticmethod
    def _is_cancelled(automation: Automation, db: Session, run: AutomationRun) -> bool:
        """True when the user asked for this run to stop.

        Checks the in-process flag first (same-worker cancel) and then the
        persisted run status, which is what makes cancellation work when the
        execute loop and the API request live in different workers.
        """
        if automation.id in _CANCEL_REQUESTED:
            return True
        try:
            db.refresh(run)
        except Exception:  # pragma: no cover - defensive
            return False
        return run.status == "cancelled"

    # ------------------------------------------------------------------
    # Single action execution (with controlled retries)
    # ------------------------------------------------------------------

    def _run_action(
        self,
        automation: Automation,
        action: Dict[str, Any],
        step: int,
        total: int,
        context: ToolExecutionContext,
        max_retries: int,
        retry_delay: float,
    ) -> Dict[str, Any]:
        tool_name = action.get("tool_name", "")
        arguments = dict(action.get("arguments") or {})
        # Ownership is always derived from the authenticated automation owner.
        for unsafe_key in _UNSAFE_ARGUMENT_KEYS:
            arguments.pop(unsafe_key, None)

        action_label = action.get("description") or tool_name
        step_log: Dict[str, Any] = {
            "step": step,
            "tool_name": tool_name,
            "description": action_label,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        # --- Static pre-flight: tool allow-list ---------------------------------
        pre_flight_error = self._pre_flight(tool_name, action)
        if pre_flight_error:
            step_log["status"] = "failed"
            step_log["error"] = pre_flight_error
            logger.warning(
                "Automation %d action %d/%d '%s' refused: %s",
                automation.id, step, total, tool_name, pre_flight_error,
            )
            return step_log

        attempts_allowed = 1 + max(0, max_retries)
        attempt = 0
        delay = max(0.0, retry_delay)
        # Only pre-approved dangerous actions may bypass the confirmation gate.
        preapproved = action.get("confirmation_policy") == "preapproved"

        while True:
            attempt += 1
            t0 = time.monotonic()
            try:
                result = tool_executor.execute(
                    tool_name=tool_name,
                    arguments=arguments,
                    context=context,
                    bypass_confirmation=preapproved,
                )
            except Exception as exc:  # unexpected executor failure
                duration_ms = round((time.monotonic() - t0) * 1000, 1)
                step_log["status"] = "exception"
                step_log["error"] = str(exc)
                step_log["duration_ms"] = duration_ms
                step_log["attempts"] = attempt
                logger.exception(
                    "Automation %d action %d '%s' raised exception.",
                    automation.id, step, tool_name,
                )
                if attempt < attempts_allowed and delay >= 0:
                    self._sleep(delay)
                    delay *= 2
                    continue
                return step_log

            duration_ms = round((time.monotonic() - t0) * 1000, 1)
            step_log["duration_ms"] = duration_ms
            step_log["attempts"] = attempt
            step_log["completed_at"] = datetime.now(timezone.utc).isoformat()

            if result.success:
                step_log["status"] = "success"
                step_log["result"] = result.data
                logger.info(
                    "Automation %d action %d/%d '%s' succeeded in %.0fms.",
                    automation.id, step, total, tool_name, duration_ms,
                )
                return step_log

            error = result.error
            if error is None:
                error_code = "UNKNOWN"
                error_message = "Unknown error"
            else:
                raw_code = getattr(error, "code", None)
                error_code = str(getattr(raw_code, "value", raw_code))
                error_message = str(getattr(error, "message", "Unknown error"))
            step_log["status"] = "failed"
            step_log["error"] = error_message
            step_log["error_code"] = error_code

            if error_code == "CONFIRMATION_REQUIRED":
                # pre_flight only lets pre-approved dangerous tools through.
                step_log["error"] = (
                    "Action requires user confirmation; it was not pre-approved "
                    "when the automation was created."
                )
                logger.warning(
                    "Automation %d action %d/%d '%s' refused: confirmation required.",
                    automation.id, step, total, tool_name,
                )
                return step_log

            retryable = (
                error_code in _RETRYABLE_ERRORS
                and attempt < attempts_allowed
            )
            if not retryable:
                logger.warning(
                    "Automation %d action %d/%d '%s' failed: %s",
                    automation.id, step, total, tool_name, step_log.get("error"),
                )
                return step_log

            logger.info(
                "Automation %d action %d/%d '%s' retrying (%d/%d) after transient failure.",
                automation.id, step, total, tool_name, attempt, max_retries,
            )
            self._sleep(delay)
            delay *= 2  # exponential backoff

    @staticmethod
    def _sleep(seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)

    @staticmethod
    def _pre_flight(tool_name: str, action: Dict[str, Any]) -> Optional[str]:
        """Static safety checks before a tool is ever invoked.

        Returns an error message, or None when the action is allowed.
        """
        if not tool_name:
            return "Action has no tool_name."
        if tool_name in AUTOMATION_BLOCKED_TOOLS:
            return f"Tool '{tool_name}' may not be used by automations."
        tool = tool_executor.registry.get_tool(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' is not registered."
        if not tool.enabled:
            return f"Tool '{tool_name}' is disabled."
        if tool.requires_confirmation and action.get("confirmation_policy") != "preapproved":
            return (
                f"Tool '{tool_name}' requires explicit user confirmation; "
                f"set confirmation_policy='preapproved' when creating the automation."
            )
        return None

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _reserve_run(
        self,
        db: Session,
        run_id: str,
        automation: Automation,
        trigger_source: str,
        execution_key: Optional[str],
    ) -> Optional[AutomationRun]:
        """Create the run row up-front so duplicate triggers are rejected.

        Returns the new run, or None when the execution key was already used.
        """
        run = AutomationRun(
            id=run_id,
            automation_id=automation.id,
            user_id=automation.user_id,
            status="running",
            trigger_source=trigger_source,
            execution_key=execution_key,
            actions_attempted=0,
            actions_completed=0,
            execution_log=[],
        )
        db.add(run)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(run)
        return run

    def _finish_run(
        self,
        db: Session,
        run: AutomationRun,
        automation: Automation,
        status: str,
        error_message: Optional[str],
        log: List[Dict[str, Any]],
        actions_attempted: int = 0,
        actions_completed: int = 0,
    ) -> AutomationRun:
        now = datetime.now(timezone.utc)
        run.status = status
        run.error_message = error_message
        run.execution_log = log
        run.actions_attempted = actions_attempted
        run.actions_completed = actions_completed
        run.completed_at = now
        automation.last_run_at = now
        db.commit()
        db.refresh(run)
        logger.info(
            "AutomationRun %s: automation=%d status=%s attempted=%d completed=%d",
            run.id, automation.id, status, actions_attempted, actions_completed,
        )
        return run

    def _persist_run(
        self,
        db: Session,
        run_id: str,
        automation: Automation,
        trigger_source: str,
        status: str,
        error_message: Optional[str],
        log: List[Dict[str, Any]],
        actions_attempted: int = 0,
        actions_completed: int = 0,
    ) -> AutomationRun:
        """Create a standalone (unguarded) run record — used by early exits."""
        now = datetime.now(timezone.utc)
        run = AutomationRun(
            id=run_id,
            automation_id=automation.id,
            user_id=automation.user_id,
            status=status,
            trigger_source=trigger_source,
            execution_key=None,
            actions_attempted=actions_attempted,
            actions_completed=actions_completed,
            execution_log=log,
            error_message=error_message,
            completed_at=now,
        )
        db.add(run)
        automation.last_run_at = now
        db.commit()
        db.refresh(run)
        logger.info(
            "AutomationRun %s: automation=%d status=%s (%s)",
            run.id, automation.id, status, error_message or "ok",
        )
        return run

    # ------------------------------------------------------------------
    # Notifications (existing RajOS notification mechanism)
    # ------------------------------------------------------------------

    def _notify(self, db: Session, automation: Automation, run: AutomationRun) -> None:
        """Inform the owner about completed / partial / failed runs."""
        if run.status not in ("completed", "partial", "failed", "cancelled"):
            return
        try:
            from app.models.user import User
            from app.notifications.notification_manager import NotificationManager

            user = db.get(User, automation.user_id)
            if user is None or not getattr(user, "notifications_enabled", False):
                return

            if run.status == "completed":
                message = (
                    f"Automation '{automation.name}' completed "
                    f"({run.actions_completed}/{run.actions_attempted} actions)."
                )
            elif run.status == "partial":
                message = (
                    f"Automation '{automation.name}' partially completed: "
                    f"{run.actions_completed}/{run.actions_attempted} actions succeeded."
                )
            elif run.status == "cancelled":
                message = f"Automation '{automation.name}' was cancelled."
            else:
                message = (
                    f"Automation '{automation.name}' failed: "
                    f"{run.error_message or 'unknown error'}"
                )

            NotificationManager().send_task_reminder(user, message)
        except Exception as exc:  # notification failure must never break a run
            logger.warning(
                "Failed to notify user about automation %d run %s: %s",
                automation.id, run.id, exc,
            )


def _user_model():
    from app.models.user import User
    return User


execution_engine = ExecutionEngine()
