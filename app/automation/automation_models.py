"""Automation Engine 2.0 — Database Models.

Expands the original Automation model with full trigger/condition/action
JSON blobs, timezone support, scheduling metadata, and an AutomationRun
table for per-execution history.
"""

import uuid
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Automation(Base):
    """Represents a user-defined automation rule."""

    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # --- Identity ---
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # --- Legacy fields (kept for backward compat) ---
    trigger = Column(String, nullable=True)   # e.g. "task.completed"
    action = Column(String, nullable=True)    # e.g. "create_task"

    # --- V2 structured trigger ---
    trigger_type = Column(
        String,
        default="schedule",
        nullable=False
    )
    # e.g. {"time": "08:00", "days": ["mon","tue"], "interval_minutes": 60,
    #        "event_type": "task.completed", "deadline_hours": 24}
    trigger_config = Column(JSON, default=dict)

    # --- V2 conditions (optional guard clauses) ---
    # e.g. [{"field": "overdue_tasks", "operator": ">", "value": 0}]
    conditions = Column(JSON, default=list)

    # --- V2 actions list (replaces single `action` string) ---
    # e.g. [{"tool_name": "get_daily_brief", "arguments": {}},
    #        {"tool_name": "create_task", "arguments": {"title": "Review"}}]
    actions = Column(JSON, default=list)

    # --- State ---
    enabled = Column(Boolean, default=True)

    # Soft-delete flag: archived automations disappear from the UI/list but
    # their execution history stays fully queryable.
    archived_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # --- Scheduling ---
    timezone = Column(String, default="Asia/Kolkata")
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)

    # --- Failure behaviour ---
    # "stop"     → abort remaining actions on first failure
    # "continue" → proceed to next action despite failure
    failure_policy = Column(String, default="stop")

    # --- Controlled retries for transient action failures ---
    max_retries = Column(Integer, default=1, nullable=False)
    retry_delay_seconds = Column(Float, default=2.0, nullable=False)

    # --- Timestamps ---
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    # --- Relationships ---
    user = relationship("User", back_populates="automations")
    runs = relationship(
        "AutomationRun",
        back_populates="automation",
        cascade="all, delete-orphan",
        order_by="AutomationRun.started_at.desc()"
    )


class AutomationRun(Base):
    """Records a single execution of an Automation."""

    __tablename__ = "automation_runs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    automation_id = Column(
        Integer,
        ForeignKey("automations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Idempotency key — a scheduler slot / event id / deadline-task pair.
    # The unique (automation_id, execution_key) constraint guarantees an
    # automation can never execute twice for the same logical trigger.
    execution_key = Column(String, nullable=True, index=True)

    # --- Outcome ---
    # "running" | "completed" | "failed" | "partial" | "skipped" | "cancelled"
    status = Column(String, default="running")

    # What triggered this run: "scheduler" | "event:<type>" | "manual"
    trigger_source = Column(String, nullable=True)

    # --- Action counters ---
    actions_attempted = Column(Integer, default=0)
    actions_completed = Column(Integer, default=0)

    # --- Detailed per-action log ---
    # e.g. [{"tool_name": "x", "status": "ok", "duration_ms": 42, "result": {...}}]
    execution_log = Column(JSON, default=list)

    # Top-level error message (if status == "failed")
    error_message = Column(Text, nullable=True)

    # --- Timestamps ---
    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    automation = relationship("Automation", back_populates="runs")

    __table_args__ = (
        UniqueConstraint(
            "automation_id", "execution_key",
            name="uq_automation_runs_automation_execution_key",
        ),
    )
