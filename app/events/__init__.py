"""RajOS V2 Real-time Events.

Exposes: EventType, BaseEvent, sse_payload, sse_event,
ConnectionManager, EventPublisher, and all event factory functions.

Event types are organized into sub-groups:
- Chat streaming (message_start, content_delta, tool calls, message_complete, error)
- Agent execution (agent_start, agent_step, agent_complete, agent_failed)
- Automation (automation_start, automation_progress, automation_complete)
- Notification (notification, mark_read, mark_all_read)
"""

from __future__ import annotations

from .event_types import (
    EventType,
    BaseEvent,
    sse_payload,
    sse_event,
    create_message_start_event,
    create_content_delta_event,
    create_tool_call_start_event,
    create_tool_call_result_event,
    create_message_complete_event,
    create_error_event,
    create_agent_start_event,
    create_agent_step_event,
    create_agent_complete_event,
    create_agent_failed_event,
    create_automation_start_event,
    create_automation_progress_event,
    create_automation_complete_event,
    create_notification_event,
)

# Connection manager — initialized on app startup
init_connection_manager = None  # type: ignore
get_connection_manager = None  # type: ignore
clear_publisher = None  # type: ignore
get_publisher = None  # type: ignore

__all__ = [
    "EventType",
    "BaseEvent",
    "sse_payload",
    "sse_event",
    "create_message_start_event",
    "create_content_delta_event",
    "create_tool_call_start_event",
    "create_tool_call_result_event",
    "create_message_complete_event",
    "create_error_event",
    "create_agent_start_event",
    "create_agent_step_event",
    "create_agent_complete_event",
    "create_agent_failed_event",
    "create_automation_start_event",
    "create_automation_progress_event",
    "create_automation_complete_event",
    "create_notification_event",
    "init_connection_manager",
    "get_connection_manager",
    "clear_publisher",
    "get_publisher",
]