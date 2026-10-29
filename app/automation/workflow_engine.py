"""Automation Engine 2.0 — Workflow Engine (Legacy Compatibility Layer).

The original WorkflowEngine is kept here as a thin façade so that any
existing code calling `workflow_engine.execute()` continues to work.
New code should use ExecutionEngine directly.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Legacy compatibility wrapper — routes named action strings to descriptive results.

    For V2 automations use ExecutionEngine which routes through the Tool Registry.
    """

    def execute(
        self,
        action: str,
        payload: dict | None = None,
    ) -> dict:
        payload = payload or {}
        logger.debug("WorkflowEngine.execute (legacy) action='%s'", action)

        known = {
            "create_task": "Task workflow triggered",
            "create_note": "Note workflow triggered",
            "send_notification": "Notification workflow triggered",
            "get_daily_brief": "Daily brief workflow triggered",
            "summarize_notes": "Note summarisation workflow triggered",
        }

        if action in known:
            return {
                "status": "success",
                "action": action,
                "message": known[action],
                "payload": payload,
            }

        return {
            "status": "error",
            "message": f"Unknown action: '{action}'. Use V2 ExecutionEngine with tool names.",
        }


workflow_engine = WorkflowEngine()
