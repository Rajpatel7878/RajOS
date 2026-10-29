"""Automation Engine 2.0 — Pydantic Schemas."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

from app.automation.trigger_engine import (
    SUPPORTED_TRIGGER_TYPES,
    trigger_engine,
    validate_timezone,
)


# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------

class TriggerConfig(BaseModel):
    """Flexible trigger configuration for all trigger types."""

    # schedule / recurring
    time: Optional[str] = None            # "08:00"
    days: Optional[List[str]] = None      # ["mon","tue","wed","thu","fri"]
    day_of_month: Optional[int] = None    # 1-31 for monthly
    cron: Optional[str] = None            # raw cron expression

    # interval
    interval_minutes: Optional[int] = None

    # event
    event_type: Optional[str] = None      # "task.completed", "task.created"

    # deadline
    deadline_hours: Optional[int] = None  # fire N hours before task due_date

    # onetime
    run_at: Optional[str] = None          # ISO-8601 datetime for one-time runs

    # condition / deadline polling cadence (minutes)
    poll_minutes: Optional[int] = None

    class Config:
        extra = "allow"  # allow unknown fields for future triggers


class ConditionRule(BaseModel):
    """A single condition that must be satisfied before actions run."""

    field: str        # e.g. "overdue_tasks", "day_of_week", "pending_tasks"
    operator: str     # "==", "!=", ">", "<", ">=", "<=", "in", "contains"
    value: Any        # compared value


class ConditionGroup(BaseModel):
    """An AND / OR / NOT group of nested conditions (max depth 3)."""

    op: str = Field(..., description="and | or | not")
    rules: List[Dict[str, Any]] = Field(..., min_length=1)


# A condition tree: flat rules are AND-ed; groups combine nested rules.
ConditionNode = Union[ConditionRule, ConditionGroup]


class ActionStep(BaseModel):
    """A single action to execute via the Tool Registry."""

    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None   # human-readable label

    # "default"     → tools that require confirmation are refused at execution
    # "preapproved" → the user explicitly pre-approved this action at creation
    confirmation_policy: str = "default"


# ---------------------------------------------------------------------------
# CRUD Schemas
# ---------------------------------------------------------------------------

class AutomationCreate(BaseModel):
    """Payload to create a new automation."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # V2 structured fields
    trigger_type: str = "schedule"       # schedule|interval|event|condition|deadline|onetime
    trigger_config: TriggerConfig = Field(default_factory=TriggerConfig)
    conditions: List[ConditionNode] = Field(default_factory=list)
    actions: List[ActionStep] = Field(default_factory=list)
    timezone: str = "Asia/Kolkata"
    failure_policy: str = "stop"         # stop | continue

    # Controlled retries for transient action failures
    max_retries: int = Field(default=1, ge=0, le=5)
    retry_delay_seconds: float = Field(default=2.0, ge=0, le=300)

    # Legacy compat (if only trigger/action strings are provided)
    trigger: Optional[str] = None
    action: Optional[str] = None

    @field_validator("timezone")
    @classmethod
    def _valid_timezone(cls, v: str) -> str:
        return validate_timezone(v)

    @field_validator("trigger_type")
    @classmethod
    def _valid_trigger_type(cls, v: str) -> str:
        if v not in SUPPORTED_TRIGGER_TYPES:
            raise ValueError(
                f"Unsupported trigger_type '{v}'. "
                f"Expected one of: {sorted(SUPPORTED_TRIGGER_TYPES)}."
            )
        return v

    @field_validator("failure_policy")
    @classmethod
    def _valid_policy(cls, v: str) -> str:
        if v not in ("stop", "continue"):
            raise ValueError("failure_policy must be 'stop' or 'continue'.")
        return v

    def validate_trigger(self) -> None:
        """Raise ValueError if the trigger definition cannot be executed."""
        trigger_engine.validate(
            self.trigger_type,
            self.trigger_config.model_dump(exclude_none=True) if self.trigger_config else {},
            self.timezone,
        )

    @field_validator("conditions")
    @classmethod
    def _valid_conditions(cls, v: List[ConditionNode]) -> List[ConditionNode]:
        """Reject malformed condition trees at request-validation time."""
        from app.automation.condition_engine import condition_engine

        condition_engine.validate([c.model_dump() for c in v or []])
        return v


class AutomationUpdate(BaseModel):
    """Payload to update an existing automation.

    Only the fields present in the payload are changed.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[TriggerConfig] = None
    conditions: Optional[List[ConditionNode]] = None
    actions: Optional[List[ActionStep]] = None
    timezone: Optional[str] = None
    failure_policy: Optional[str] = None
    enabled: Optional[bool] = None
    max_retries: Optional[int] = Field(default=None, ge=0, le=5)
    retry_delay_seconds: Optional[float] = Field(default=None, ge=0, le=300)

    # Legacy compat
    trigger: Optional[str] = None
    action: Optional[str] = None

    @field_validator("timezone")
    @classmethod
    def _valid_timezone(cls, v: Optional[str]) -> Optional[str]:
        return validate_timezone(v) if v is not None else v

    @field_validator("trigger_type")
    @classmethod
    def _valid_trigger_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in SUPPORTED_TRIGGER_TYPES:
            raise ValueError(
                f"Unsupported trigger_type '{v}'. "
                f"Expected one of: {sorted(SUPPORTED_TRIGGER_TYPES)}."
            )
        return v

    @field_validator("failure_policy")
    @classmethod
    def _valid_policy(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("stop", "continue"):
            raise ValueError("failure_policy must be 'stop' or 'continue'.")
        return v

    @field_validator("conditions")
    @classmethod
    def _valid_conditions(
        cls, v: Optional[List[ConditionNode]]
    ) -> Optional[List[ConditionNode]]:
        if v is None:
            return v
        from app.automation.condition_engine import condition_engine

        condition_engine.validate([c.model_dump() for c in v])
        return v


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class AutomationResponse(BaseModel):
    """Full automation record returned by the API."""

    id: int
    name: str
    description: Optional[str] = None

    trigger_type: str
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None

    timezone: str
    failure_policy: str
    enabled: bool
    max_retries: int = 1
    retry_delay_seconds: float = 2.0

    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Legacy fields
    trigger: Optional[str] = None
    action: Optional[str] = None

    @field_validator(
        "next_run_at", "last_run_at", "created_at", "updated_at"
    )
    @classmethod
    def _tz_aware(cls, v: Optional[datetime]) -> Optional[datetime]:
        # SQLite returns naive datetimes — they are stored as UTC.
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    class Config:
        from_attributes = True


class AutomationRunResponse(BaseModel):
    """Execution history record."""

    id: str
    automation_id: int
    user_id: int
    status: str
    trigger_source: Optional[str] = None
    actions_attempted: int
    actions_completed: int
    execution_log: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    execution_key: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    @field_validator("started_at", "completed_at")
    @classmethod
    def _tz_aware_run(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    class Config:
        from_attributes = True


class AutomationPreview(BaseModel):
    """Preview response — next scheduled time + expected actions."""

    automation_id: int
    next_run_at: Optional[datetime]
    actions: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]]
    estimated_action_count: int
    timezone: str


# ---------------------------------------------------------------------------
# Event Schema (legacy + V2)
# ---------------------------------------------------------------------------

class AutomationEvent(BaseModel):
    """An event that can trigger event-based automations.

    The payload is opaque data for the caller: it is never used to decide
    ownership, permissions or which actions run.  ``type`` is length-capped so
    a caller cannot inflate the stored execution/idempotency keys.
    """

    type: str = Field(..., min_length=1, max_length=120)  # e.g. "task.completed"
    message: Optional[str] = Field(None, max_length=500)
    payload: Optional[Dict[str, Any]] = None
