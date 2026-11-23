"""Typed event types for RajOS V2 real-time system.

All event classes use dataclasses with ALL fields having default values,
which avoids Python dataclass initialization ordering restrictions.
Events are created via factory functions for best results.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from enum import Enum


class EventType(str, Enum):
    """Typed event types for the real-time system."""

    # Chat streaming events
    MESSAGE_START = "message_start"
    CONTENT_DELTA = "content_delta"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_RESULT = "tool_call_result"
    MESSAGE_COMPLETE = "message_complete"
    ERROR = "error"
    CANCELLED = "cancelled"

    # Agent execution events
    AGENT_START = "agent_start"
    AGENT_PROGRESS = "agent_progress"
    AGENT_STEP = "agent_step"
    AGENT_COMPLETE = "agent_complete"
    AGENT_FAILED = "agent_failed"
    AGENT_CANCELLED = "agent_cancelled"

    # Automation events
    AUTOMATION_START = "automation_start"
    AUTOMATION_PROGRESS = "automation_progress"
    AUTOMATION_COMPLETE = "automation_complete"
    AUTOMATION_FAILED = "automation_failed"
    AUTOMATION_CANCELLED = "automation_cancelled"

    # Notification events
    NOTIFICATION = "notification"
    MARK_READ = "mark_read"
    MARK_ALL_READ = "mark_all_read"

    # System/events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"
    RECONNECT = "reconnect"


def _now() -> float:
    return time.time()


def _uuid() -> str:
    return str(uuid4())


# ---------------------------------------------------------------------------
# Base event — all fields have defaults, no inheritance issues
# ---------------------------------------------------------------------------

@dataclass
class BaseEvent:
    """Base event with ALL fields having default values.

    This avoids the Python dataclass initialization ordering restriction
    where parameters without defaults must come before parameters with defaults.
    """

    event_type: EventType = EventType.ERROR
    user_id: int = 0
    event_id: str = field(default_factory=_uuid)
    timestamp: float = field(default_factory=_now)
    conversation_id: Optional[str] = None
    execution_id: Optional[str] = None
    message_id: Optional[str] = None
    agent_id: Optional[str] = None
    automation_id: Optional[int] = None
    tool_name: Optional[str] = None
    tool_description: Optional[str] = None
    tool_safe_description: Optional[str] = None
    success: Optional[bool] = None
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    final_text: Optional[str] = None
    delta: Optional[str] = None
    is_final: Optional[bool] = None
    title: Optional[str] = None
    message: Optional[str] = None
    category: str = "system"
    navigation_target: Optional[str] = None
    read: bool = False


# ---------------------------------------------------------------------------
# Chat Streaming Events
# ---------------------------------------------------------------------------

@dataclass
class MessageStartEvent(BaseEvent):
    """Sent when a new AI message starts streaming.

    Creates with factory function: create_message_start_event(...)
    """

    event_type: EventType = EventType.MESSAGE_START
    conversation_id: str = ""
    message_id: str = ""
    agent_id: str = ""


def create_message_start_event(
    conversation_id: str,
    message_id: str,
    agent_id: str,
    user_id: int,
) -> MessageStartEvent:
    """Factory for MessageStartEvent."""
    return MessageStartEvent(
        event_type=EventType.MESSAGE_START,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        agent_id=agent_id,
    )


@dataclass
class ContentDeltaEvent(BaseEvent):
    """Sent when a content chunk arrives progressively."""

    event_type: EventType = EventType.CONTENT_DELTA
    conversation_id: str = ""
    message_id: str = ""
    delta: str = ""
    is_final: bool = False


def create_content_delta_event(
    conversation_id: str,
    message_id: str,
    delta: str,
    is_final: bool = False,
    user_id: int = 0,
) -> ContentDeltaEvent:
    """Factory for ContentDeltaEvent."""
    return ContentDeltaEvent(
        event_type=EventType.CONTENT_DELTA,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        delta=delta,
        is_final=is_final,
    )


@dataclass
class ToolCallStartEvent(BaseEvent):
    """Sent when a tool call starts execution."""

    event_type: EventType = EventType.TOOL_CALL_START
    conversation_id: str = ""
    message_id: str = ""
    tool_name: str = ""
    tool_description: str = ""
    safety_sanitized: bool = True


def create_tool_call_start_event(
    conversation_id: str,
    message_id: str,
    tool_name: str,
    tool_description: str,
    user_id: int,
    safety_sanitized: bool = True,
) -> ToolCallStartEvent:
    """Factory for ToolCallStartEvent."""
    return ToolCallStartEvent(
        event_type=EventType.TOOL_CALL_START,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        tool_name=tool_name,
        tool_description=tool_description,
        safety_sanitized=safety_sanitized,
    )


@dataclass
class ToolCallResultEvent(BaseEvent):
    """Sent when a tool execution completes."""

    event_type: EventType = EventType.TOOL_CALL_RESULT
    conversation_id: str = ""
    message_id: str = ""
    tool_name: str = ""
    tool_safe_description: str = ""
    success: bool = False
    result_summary: Optional[str] = None
    error_message: Optional[str] = None


def create_tool_call_result_event(
    conversation_id: str,
    message_id: str,
    tool_name: str,
    success: bool,
    user_id: int,
    result_summary: Optional[str] = None,
    error_message: Optional[str] = None,
) -> ToolCallResultEvent:
    """Factory for ToolCallResultEvent."""
    return ToolCallResultEvent(
        event_type=EventType.TOOL_CALL_RESULT,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        tool_name=tool_name,
        success=success,
        result_summary=result_summary,
        error_message=error_message,
    )


@dataclass
class MessageCompleteEvent(BaseEvent):
    """Sent when the complete message is ready."""

    event_type: EventType = EventType.MESSAGE_COMPLETE
    conversation_id: str = ""
    message_id: str = ""
    final_text: str = ""
    markdown: bool = True


def create_message_complete_event(
    conversation_id: str,
    message_id: str,
    final_text: str,
    user_id: int,
    markdown: bool = True,
) -> MessageCompleteEvent:
    """Factory for MessageCompleteEvent."""
    return MessageCompleteEvent(
        event_type=EventType.MESSAGE_COMPLETE,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        final_text=final_text,
        markdown=markdown,
    )


@dataclass
class ErrorEvent(BaseEvent):
    """Sent when an error occurs."""

    event_type: EventType = EventType.ERROR
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    error_code: str = "unknown_error"
    error_message: str = "An unexpected error occurred"


def create_error_event(
    user_id: int,
    conversation_id: Optional[str] = None,
    message_id: Optional[str] = None,
    error_code: str = "unknown_error",
    error_message: str = "An unexpected error occurred",
) -> ErrorEvent:
    """Factory for ErrorEvent."""
    return ErrorEvent(
        event_type=EventType.ERROR,
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        error_code=error_code,
        error_message=error_message,
    )


# ---------------------------------------------------------------------------
# Agent Execution Events
# ---------------------------------------------------------------------------

@dataclass
class AgentStartEvent(BaseEvent):
    """Sent when agent execution starts."""

    event_type: EventType = EventType.AGENT_START
    agent_id: str = ""
    agent_name: str = ""
    conversation_id: str = ""


def create_agent_start_event(
    agent_id: str,
    agent_name: str,
    conversation_id: str,
    user_id: int,
) -> AgentStartEvent:
    """Factory for AgentStartEvent."""
    return AgentStartEvent(
        event_type=EventType.AGENT_START,
        user_id=user_id,
        agent_id=agent_id,
        agent_name=agent_name,
        conversation_id=conversation_id,
    )


@dataclass
class AgentStepEvent(BaseEvent):
    """Sent when an agent takes a step."""

    event_type: EventType = EventType.AGENT_STEP
    agent_id: str = ""
    step: int = 0
    total_steps: int = 0
    current_tool: str = ""
    status: str = "running"
    conversation_id: str = ""


def create_agent_step_event(
    agent_id: str,
    step: int,
    total_steps: int,
    current_tool: str,
    status: str,
    conversation_id: str,
    user_id: int,
) -> AgentStepEvent:
    """Factory for AgentStepEvent."""
    return AgentStepEvent(
        event_type=EventType.AGENT_STEP,
        user_id=user_id,
        agent_id=agent_id,
        step=step,
        total_steps=total_steps,
        current_tool=current_tool,
        status=status,
        conversation_id=conversation_id,
    )


@dataclass
class AgentCompleteEvent(BaseEvent):
    """Sent when agent execution completes."""

    event_type: EventType = EventType.AGENT_COMPLETE
    agent_id: str = ""
    agent_name: str = ""
    conversation_id: str = ""
    final_response: str = ""
    status: str = "completed"


def create_agent_complete_event(
    agent_id: str,
    agent_name: str,
    conversation_id: str,
    final_response: str,
    user_id: int,
) -> AgentCompleteEvent:
    """Factory for AgentCompleteEvent."""
    return AgentCompleteEvent(
        event_type=EventType.AGENT_COMPLETE,
        user_id=user_id,
        agent_id=agent_id,
        agent_name=agent_name,
        conversation_id=conversation_id,
        final_response=final_response,
    )


@dataclass
class AgentFailedEvent(BaseEvent):
    """Sent when agent execution fails."""

    event_type: EventType = EventType.AGENT_FAILED
    agent_id: str = ""
    agent_name: str = ""
    conversation_id: str = ""
    error_message: str = ""


def create_agent_failed_event(
    agent_id: str,
    agent_name: str,
    conversation_id: str,
    error_message: str,
    user_id: int,
) -> AgentFailedEvent:
    """Factory for AgentFailedEvent."""
    return AgentFailedEvent(
        event_type=EventType.AGENT_FAILED,
        user_id=user_id,
        agent_id=agent_id,
        agent_name=agent_name,
        conversation_id=conversation_id,
        error_message=error_message,
    )


# ---------------------------------------------------------------------------
# Automation Events
# ---------------------------------------------------------------------------

@dataclass
class AutomationStartEvent(BaseEvent):
    """Sent when automation execution starts."""

    event_type: EventType = EventType.AUTOMATION_START
    automation_id: int = 0
    automation_name: str = ""
    conversation_id: str = ""


def create_automation_start_event(
    automation_id: int,
    automation_name: str,
    user_id: int,
    conversation_id: str = "",
) -> AutomationStartEvent:
    """Factory for AutomationStartEvent."""
    return AutomationStartEvent(
        event_type=EventType.AUTOMATION_START,
        user_id=user_id,
        automation_id=automation_id,
        automation_name=automation_name,
        conversation_id=conversation_id,
    )


@dataclass
class AutomationProgressEvent(BaseEvent):
    """Sent when automation makes progress."""

    event_type: EventType = EventType.AUTOMATION_PROGRESS
    automation_id: int = 0
    step: int = 0
    status: str = "running"
    result_summary: str = ""


def create_automation_progress_event(
    automation_id: int,
    step: int,
    status: str,
    result_summary: str,
    user_id: int,
) -> AutomationProgressEvent:
    """Factory for AutomationProgressEvent."""
    return AutomationProgressEvent(
        event_type=EventType.AUTOMATION_PROGRESS,
        user_id=user_id,
        automation_id=automation_id,
        step=step,
        status=status,
        result_summary=result_summary,
    )


@dataclass
class AutomationCompleteEvent(BaseEvent):
    """Sent when automation completes."""

    event_type: EventType = EventType.AUTOMATION_COMPLETE
    automation_id: int = 0
    automation_name: str = ""
    status: str = "completed"
    actions_completed: int = 0
    actions_total: int = 0


def create_automation_complete_event(
    automation_id: int,
    automation_name: str,
    status: str,
    actions_completed: int,
    actions_total: int,
    user_id: int,
) -> AutomationCompleteEvent:
    """Factory for AutomationCompleteEvent."""
    return AutomationCompleteEvent(
        event_type=EventType.AUTOMATION_COMPLETE,
        user_id=user_id,
        automation_id=automation_id,
        automation_name=automation_name,
        status=status,
        actions_completed=actions_completed,
        actions_total=actions_total,
    )


# ---------------------------------------------------------------------------
# Notification Events
# ---------------------------------------------------------------------------

@dataclass
class NotificationEvent(BaseEvent):
    """Sent for in-app notifications."""

    event_type: EventType = EventType.NOTIFICATION
    title: str = ""
    message: str = ""
    category: str = "system"
    navigation_target: str = ""
    read: bool = False


def create_notification_event(
    user_id: int,
    title: str,
    message: str,
    category: str = "system",
    navigation_target: str = "",
    read: bool = False,
) -> NotificationEvent:
    """Factory for NotificationEvent."""
    return NotificationEvent(
        event_type=EventType.NOTIFICATION,
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        navigation_target=navigation_target,
        read=read,
    )


# ---------------------------------------------------------------------------
# SSE Payload Helpers
# ---------------------------------------------------------------------------

def sse_payload(event: BaseEvent) -> str:
    """Serialize a BaseEvent to an SSE-compatible JSON string."""
    data = {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp,
        "user_id": event.user_id,
    }
    # Include only non-default fields for clean SSE output
    # Defaults: event_type=ERROR, user_id=0, event_id=uuid, timestamp=time
    optional_fields = {
        "conversation_id": event.conversation_id,
        "execution_id": event.execution_id,
        "message_id": event.message_id,
        "agent_id": event.agent_id,
        "automation_id": event.automation_id,
        "tool_name": event.tool_name,
        "tool_description": event.tool_description,
        "tool_safe_description": event.tool_safe_description,
        "success": event.success,
        "result_summary": event.result_summary,
        "error_message": event.error_message,
        "final_text": event.final_text,
        "delta": event.delta,
        "is_final": event.is_final,
        "title": event.title,
        "message": event.message,
        "category": event.category if event.category != "system" else None,
        "navigation_target": event.navigation_target,
        "read": event.read if event.read is not False else None,
    }
    for key, value in optional_fields.items():
        if value is not None and value != "" and value != False:
            data[key] = value
    # Also include if explicitly set to True/False
    if event.read is not False:
        data["read"] = event.read
    return json.dumps(data, default=str)


def sse_event(event_type: EventType, data: str, id: Optional[str] = None) -> str:
    """Build a complete SSE formatted string."""
    markers = ""
    if id:
        markers += f"id: {id}\n"
    markers += f"event: {event_type}\n"
    markers += f"data: {data}\n\n"
    return markers