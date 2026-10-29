"""Automation Engine 2.0 — Automation-facing Tools.

Tools that let the AI Core / Agent System work with the Automation Engine:

  * ``create_automation``  — turns a natural-language request into a structured
    automation.  Requires confirmation, so the AI can never silently commit a
    recurring action (Phase 6 confirmation flow).
  * ``send_notification``  — notify the user via the existing RajOS
    notification mechanism (used as an automation action).
  * ``run_agent``          — trigger an approved agent under stricter limits
    when called from an automation (step cap, timeout cap, ownership check).

Ownership is ALWAYS derived from ``context.user_id`` (the authenticated user).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.database.connection import SessionLocal
from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext

logger = logging.getLogger(__name__)

# Stricter ceilings for automation-triggered agents.
_AUTOMATION_MAX_STEPS = 3
_AUTOMATION_TIMEOUT_SECONDS = 30.0


# ---------------------------------------------------------------------------
# create_automation
# ---------------------------------------------------------------------------

class CreateAutomationInput(BaseModel):
    """Structured automation proposal produced by the AI."""

    name: str = Field(..., min_length=1, max_length=120, description="Automation name")
    description: Optional[str] = Field(None, max_length=500)

    trigger_type: str = Field(
        default="schedule",
        description="schedule | interval | onetime | event | condition | deadline",
    )
    trigger_config: Dict[str, Any] = Field(
        default_factory=dict,
        description='e.g. {"time": "08:00", "days": ["mon","tue"]}',
    )
    conditions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='Optional guards, e.g. [{"field":"overdue_tasks","operator":">","value":0}]',
    )
    actions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='Ordered tool actions, e.g. [{"tool_name":"create_note","arguments":{...}}]',
    )
    timezone: str = Field(default="Asia/Kolkata", description="IANA timezone")
    failure_policy: str = Field(default="stop", description="stop | continue")

    @field_validator("failure_policy")
    @classmethod
    def _policy(cls, v: str) -> str:
        if v not in ("stop", "continue"):
            raise ValueError("failure_policy must be 'stop' or 'continue'.")
        return v


class CreateAutomationTool(ToolDefinition):
    name = "create_automation"
    description = (
        "Create a structured automation (schedule / event / deadline trigger with "
        "conditions and tool actions). Always show the user the parsed automation "
        "for confirmation before calling this tool."
    )
    category = ToolCategory.SYSTEM
    read_only = False
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = True          # never silently create recurring actions
    required_permissions = ["automation.write"]
    args_model = CreateAutomationInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        from app.automation.automation_schemas import (
            AutomationCreate, ActionStep, ConditionRule, TriggerConfig,
        )
        from app.automation.automation_service import automation_service

        args = CreateAutomationInput(**arguments)

        payload = AutomationCreate(
            name=args.name,
            description=args.description,
            trigger_type=args.trigger_type,
            trigger_config=TriggerConfig(**args.trigger_config),
            conditions=[ConditionRule(**c) for c in args.conditions],
            actions=[ActionStep(**a) for a in args.actions],
            timezone=args.timezone,
            failure_policy=args.failure_policy,
        )

        db = SessionLocal()
        try:
            # Ownership comes from the authenticated context, never from args.
            automation = automation_service.create(db, context.user_id, payload)
            return {
                "automation_id": automation.id,
                "name": automation.name,
                "trigger_type": automation.trigger_type,
                "trigger_config": automation.trigger_config,
                "timezone": automation.timezone,
                "enabled": automation.enabled,
                "next_run_at": automation.next_run_at.isoformat()
                if automation.next_run_at else None,
                "actions": automation.actions,
                "message": "Automation created.",
            }
        finally:
            db.close()


# ---------------------------------------------------------------------------
# send_notification
# ---------------------------------------------------------------------------

class SendNotificationInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Notification text")
    title: Optional[str] = Field(None, max_length=120, description="Optional title")


class SendNotificationTool(ToolDefinition):
    name = "send_notification"
    description = "Send a notification to the authenticated user via the RajOS notification system."
    category = ToolCategory.SYSTEM
    read_only = False
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["notifications.write"]
    args_model = SendNotificationInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        from app.models.user import User
        from app.notifications.notification_manager import NotificationManager

        args = SendNotificationInput(**arguments)
        db = SessionLocal()
        try:
            user = db.get(User, context.user_id)
            if user is None:
                raise ValueError("User not found.")
            if not user.notifications_enabled:
                return {
                    "status": "skipped",
                    "reason": "notifications_disabled",
                    "message": args.message,
                }

            text = args.message if not args.title else f"{args.title}: {args.message}"
            result = NotificationManager().send_task_reminder(user, text)
            return {"status": "sent", "channel_result": result, "message": args.message}
        finally:
            db.close()


# ---------------------------------------------------------------------------
# run_agent
# ---------------------------------------------------------------------------

class RunAgentInput(BaseModel):
    agent_id: str = Field(..., min_length=1, description="Approved agent id")
    prompt: str = Field(..., min_length=1, max_length=4000, description="Task for the agent")
    max_steps: Optional[int] = Field(
        None, ge=1, le=5, description="Optional stricter step cap"
    )


class RunAgentTool(ToolDefinition):
    name = "run_agent"
    description = (
        "Run an approved RajOS agent with a prompt. Bounded by the agent's step, "
        "tool-call and timeout limits (tighter caps apply inside automations)."
    )
    category = ToolCategory.SYSTEM
    read_only = False
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = False
    required_permissions = ["agents.run"]
    args_model = RunAgentInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        from app.agents.agent_registry import agent_registry
        from app.agents.agent_service import agent_service

        args = RunAgentInput(**arguments)

        db = SessionLocal()
        try:
            # Ownership check — a user can only run their own agents.
            agent = agent_registry.get_agent(db, args.agent_id, context.user_id)
            if agent is None:
                raise ValueError(f"Agent '{args.agent_id}' was not found.")
            if not agent.enabled:
                raise ValueError(f"Agent '{agent.name}' is disabled.")

            from_automation = context.metadata.get("source") == "automation"
            max_steps_override = args.max_steps
            timeout_override = None

            if from_automation:
                # Automation-triggered agents are held to stricter limits.
                ceiling = min(_AUTOMATION_MAX_STEPS, agent.max_steps or _AUTOMATION_MAX_STEPS)
                max_steps_override = (
                    min(max_steps_override, ceiling)
                    if max_steps_override else ceiling
                )
                timeout_override = min(
                    _AUTOMATION_TIMEOUT_SECONDS, agent.timeout_seconds or _AUTOMATION_TIMEOUT_SECONDS
                )

            return agent_service.run_agent(
                db=db,
                agent_id=args.agent_id,
                user_id=context.user_id,
                prompt=args.prompt,
                max_steps_override=max_steps_override,
                timeout_seconds_override=timeout_override,
            )
        finally:
            db.close()
