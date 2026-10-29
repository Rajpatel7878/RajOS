"""Automation Engine 2.0 — Trigger Engine.

Computes next_run_at for every time-based trigger type in the automation's
own timezone (never server-local time), and matches event triggers.

All timestamps are stored internally as timezone-aware UTC datetimes, but
schedule arithmetic ("every day at 08:00") is performed in the automation's
configured timezone so daylight-saving transitions and user-local intent are
preserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Day-name → weekday index (Monday=0)
_DAY_MAP = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3,
    "fri": 4, "sat": 5, "sun": 6,
}

# Every trigger type the engine understands.
SUPPORTED_TRIGGER_TYPES = {
    "schedule",   # daily / specific days / monthly at a local time
    "interval",   # every N minutes
    "onetime",    # a single absolute datetime
    "event",      # fired by the event dispatcher
    "condition",  # polled; runs only when its conditions are satisfied
    "deadline",   # polled; runs N hours before a task's due date
}

# Time-based types the scheduler polls.
SCHEDULER_TRIGGER_TYPES = ("schedule", "interval", "onetime", "condition", "deadline")

# How often condition/deadline triggers are polled (minutes) unless overridden.
_DEFAULT_POLL_MINUTES = 15


def load_timezone(name: Optional[str]) -> ZoneInfo:
    """Resolve an IANA timezone name, raising ValueError for unknown zones."""
    tz_name = (name or "UTC").strip()
    try:
        return ZoneInfo(tz_name)
    except Exception as exc:  # ZoneInfoNotFoundError / ValueError
        raise ValueError(f"Unsupported timezone '{tz_name}'.") from exc


def validate_timezone(name: Optional[str]) -> str:
    """Validate a timezone name and return it normalised (raises ValueError)."""
    tz_name = (name or "UTC").strip()
    load_timezone(tz_name)
    return tz_name


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime) -> datetime:
    """Treat naive datetimes as UTC (storage convention)."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _parse_time(time_str: str) -> tuple[int, int]:
    """Parse 'HH:MM' → (hour, minute) integers."""
    parts = str(time_str).strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid time '{time_str}' — expected HH:MM.")
    return int(parts[0]), int(parts[1])


class TriggerEngine:
    """Calculates next_run_at and matches event triggers."""

    # ------------------------------------------------------------------
    # Public: compute next_run_at from trigger_type + trigger_config
    # ------------------------------------------------------------------

    def compute_next_run(
        self,
        trigger_type: str,
        trigger_config: Dict[str, Any],
        after: Optional[datetime] = None,
        timezone_name: Optional[str] = None,
    ) -> Optional[datetime]:
        """Return the next UTC datetime this trigger should fire.

        Args:
            trigger_type:    One of SUPPORTED_TRIGGER_TYPES.
            trigger_config:  The trigger configuration blob.
            after:           Reference moment (defaults to now, UTC).
            timezone_name:   IANA timezone the schedule is expressed in.

        Returns None for event triggers (they fire on demand).
        """
        after = _as_utc(after or _now_utc())
        cfg = trigger_config or {}

        if trigger_type == "schedule":
            return self._next_schedule(cfg, after, timezone_name)

        if trigger_type == "interval":
            return self._next_interval(cfg, after)

        if trigger_type == "onetime":
            return self._next_onetime(cfg, after, timezone_name)

        if trigger_type == "condition":
            # Polled trigger — the scheduler re-checks it on a fixed cadence.
            return after + timedelta(minutes=self._poll_minutes(cfg))

        if trigger_type == "deadline":
            # Polled trigger — the scheduler scans upcoming task due dates.
            return after + timedelta(minutes=self._poll_minutes(cfg))

        if trigger_type == "event":
            return None  # not time-based; the event dispatcher handles these

        logger.warning("Unknown trigger_type '%s'", trigger_type)
        return None

    # ------------------------------------------------------------------
    # Public: match an event against a trigger config
    # ------------------------------------------------------------------

    def matches_event(
        self,
        trigger_type: str,
        trigger_config: Dict[str, Any],
        event_type: str,
    ) -> bool:
        """Return True if this automation's event trigger matches the fired event."""
        if trigger_type != "event":
            return False
        configured = (trigger_config or {}).get("event_type", "")
        return bool(configured) and configured == event_type

    def validate(
        self,
        trigger_type: str,
        trigger_config: Dict[str, Any],
        timezone_name: Optional[str] = None,
    ) -> None:
        """Raise ValueError when a trigger definition is not executable."""
        if trigger_type not in SUPPORTED_TRIGGER_TYPES:
            raise ValueError(
                f"Unsupported trigger_type '{trigger_type}'. "
                f"Expected one of: {sorted(SUPPORTED_TRIGGER_TYPES)}."
            )
        cfg = trigger_config or {}
        validate_timezone(timezone_name)

        if trigger_type == "schedule":
            if not cfg.get("time"):
                raise ValueError("Schedule trigger requires a 'time' (HH:MM) field.")
            _parse_time(str(cfg.get("time")))
            for day in cfg.get("days") or []:
                if day not in _DAY_MAP:
                    raise ValueError(f"Invalid weekday '{day}' in schedule trigger.")
            dom = cfg.get("day_of_month")
            if dom is not None and not (1 <= int(dom) <= 31):
                raise ValueError("'day_of_month' must be between 1 and 31.")
        elif trigger_type == "interval":
            minutes = cfg.get("interval_minutes")
            if not isinstance(minutes, (int, float)) or minutes <= 0:
                raise ValueError("Interval trigger requires 'interval_minutes' > 0.")
        elif trigger_type == "onetime":
            if not cfg.get("run_at"):
                raise ValueError("One-time trigger requires a 'run_at' datetime.")
            try:
                datetime.fromisoformat(str(cfg.get("run_at")))
            except ValueError as exc:
                raise ValueError(f"Invalid 'run_at' datetime: {exc}") from exc
        elif trigger_type == "event":
            if not cfg.get("event_type"):
                raise ValueError("Event trigger requires an 'event_type'.")
        elif trigger_type == "deadline":
            hours = cfg.get("deadline_hours")
            if hours is not None and (not isinstance(hours, (int, float)) or hours <= 0):
                raise ValueError("'deadline_hours' must be > 0.")

    # ------------------------------------------------------------------
    # Schedule triggers (timezone aware)
    # ------------------------------------------------------------------

    def _next_schedule(
        self,
        cfg: Dict[str, Any],
        after: datetime,
        timezone_name: Optional[str],
    ) -> Optional[datetime]:
        """Daily / specific-days / monthly schedule, computed in user timezone."""
        time_str = cfg.get("time")
        if not time_str:
            logger.warning("schedule trigger missing 'time' field")
            return None

        tz = load_timezone(timezone_name)
        hour, minute = _parse_time(str(time_str))
        days: List[str] = cfg.get("days") or []   # e.g. ["mon","wed","fri"]
        day_of_month: Optional[int] = cfg.get("day_of_month")

        # Work entirely in the automation's local timezone.
        after_local = after.astimezone(tz)

        candidate = after_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= after_local:
            candidate += timedelta(days=1)

        if day_of_month is not None:
            # Monthly: advance (local days) until day_of_month matches.
            for _ in range(62):
                if candidate.day == day_of_month:
                    return candidate.astimezone(timezone.utc)
                candidate += timedelta(days=1)
            # day_of_month 29-31 can be unreachable in short months; keep polling
            # monthly — the scheduler will retry on the next evaluation window.
            logger.warning(
                "day_of_month %s not reached in the current month window.", day_of_month
            )
            return None

        if days:
            target_weekdays = {_DAY_MAP[d] for d in days if d in _DAY_MAP}
            for _ in range(8):
                if candidate.weekday() in target_weekdays:
                    return candidate.astimezone(timezone.utc)
                candidate += timedelta(days=1)
            return None

        # Every day
        return candidate.astimezone(timezone.utc)

    def _next_interval(
        self,
        cfg: Dict[str, Any],
        after: datetime,
    ) -> Optional[datetime]:
        """Interval trigger: every N minutes from the reference moment."""
        minutes = cfg.get("interval_minutes")
        if not minutes or not isinstance(minutes, (int, float)) or minutes <= 0:
            logger.warning("interval trigger has invalid interval_minutes: %s", minutes)
            return None
        return after + timedelta(minutes=int(minutes))

    def _next_onetime(
        self,
        cfg: Dict[str, Any],
        after: datetime,
        timezone_name: Optional[str],
    ) -> Optional[datetime]:
        """One-time trigger: fire at a specific ISO-8601 datetime.

        A naive datetime is interpreted in the automation's timezone.
        """
        run_at_str = cfg.get("run_at")
        if not run_at_str:
            return None
        try:
            run_at = datetime.fromisoformat(str(run_at_str))
        except ValueError as exc:
            logger.error("onetime trigger: invalid run_at '%s': %s", run_at_str, exc)
            return None

        if run_at.tzinfo is None:
            tz = load_timezone(timezone_name)
            run_at = run_at.replace(tzinfo=tz)
        run_at_utc = run_at.astimezone(timezone.utc)
        return run_at_utc if run_at_utc > after else None

    # ------------------------------------------------------------------
    # Deadline / condition polling helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _poll_minutes(cfg: Dict[str, Any]) -> int:
        minutes = cfg.get("poll_minutes")
        if isinstance(minutes, (int, float)) and minutes > 0:
            return int(minutes)
        return _DEFAULT_POLL_MINUTES

    def deadline_fires(
        self,
        cfg: Dict[str, Any],
        due_date: datetime,
    ) -> bool:
        """Return True if now is within the deadline_hours window before due_date."""
        hours = cfg.get("deadline_hours", 24)
        now = _now_utc()
        due_date = _as_utc(due_date)
        fire_at = due_date - timedelta(hours=float(hours))
        return fire_at <= now < due_date


trigger_engine = TriggerEngine()
