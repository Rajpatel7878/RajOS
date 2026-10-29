"""Automation Engine 2.0 — API Router.

Endpoints:
  POST   /automation/                  Create
  GET    /automation/                  List
  GET    /automation/{id}              Get one
  PUT    /automation/{id}              Update
  DELETE /automation/{id}              Delete
  POST   /automation/{id}/enable       Enable
  POST   /automation/{id}/disable      Disable
  POST   /automation/{id}/run          Manual run
  POST   /automation/{id}/cancel       Cancel an in-flight run
  GET    /automation/{id}/runs         Execution history
  GET    /automation/{id}/preview      Preview next run + actions
  POST   /automation/preview           Preview a draft before creating it
  POST   /automation/event             Fire event (internal / testing)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.automation.automation_schemas import (
    AutomationCreate,
    AutomationUpdate,
    AutomationResponse,
    AutomationRunResponse,
    AutomationPreview,
    AutomationEvent,
)
from app.automation.automation_service import automation_service
from app.automation.trigger_engine import trigger_engine
from app.models.user import User
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/automation", tags=["Automation"])


def _get_automation_or_404(
    automation_id: int,
    user: User,
    db: Session,
    include_archived: bool = False,
):
    # Ownership is always derived from the authenticated user — never from
    # any user-supplied value.
    automation = automation_service.get_one(
        db, user.id, automation_id, include_archived=include_archived
    )
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found.")
    return automation


# ------------------------------------------------------------------
# CRUD
# ------------------------------------------------------------------

@router.post("/", response_model=AutomationResponse, status_code=201)
def create_automation(
    data: AutomationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new automation (validated server-side)."""
    try:
        return automation_service.create(db, user.id, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/", response_model=list[AutomationResponse])
def list_automations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all automations for the authenticated user."""
    return automation_service.get_all(db, user.id)


@router.get("/{automation_id}", response_model=AutomationResponse)
def get_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single automation by ID."""
    return _get_automation_or_404(automation_id, user, db)


@router.put("/{automation_id}", response_model=AutomationResponse)
def update_automation(
    automation_id: int,
    data: AutomationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update an existing automation."""
    automation = _get_automation_or_404(automation_id, user, db)
    try:
        return automation_service.update(db, automation, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/{automation_id}")
def delete_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete (archive) an automation — its execution history is preserved."""
    automation = _get_automation_or_404(automation_id, user, db)
    return automation_service.delete(db, automation)


# ------------------------------------------------------------------
# Enable / Disable
# ------------------------------------------------------------------

@router.post("/{automation_id}/enable", response_model=AutomationResponse)
def enable_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enable an automation (also recomputes next_run_at)."""
    automation = _get_automation_or_404(automation_id, user, db)
    return automation_service.enable(db, automation)


@router.post("/{automation_id}/disable", response_model=AutomationResponse)
def disable_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Disable an automation."""
    automation = _get_automation_or_404(automation_id, user, db)
    return automation_service.disable(db, automation)


# ------------------------------------------------------------------
# Manual Run
# ------------------------------------------------------------------

@router.post("/{automation_id}/run", response_model=AutomationRunResponse)
def run_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Immediately execute an automation regardless of its schedule."""
    automation = _get_automation_or_404(automation_id, user, db)
    run = automation_service.run_now(db, automation)
    return run


@router.post("/{automation_id}/cancel")
def cancel_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cancel the automation's in-flight run (remaining actions are skipped)."""
    automation = _get_automation_or_404(automation_id, user, db)
    return automation_service.cancel(db, automation)


# ------------------------------------------------------------------
# Execution History
# ------------------------------------------------------------------

@router.get("/{automation_id}/runs", response_model=list[AutomationRunResponse])
def get_automation_runs(
    automation_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get execution history for an automation (readable after deletion)."""
    # Verify ownership — archived automations keep readable history.
    _get_automation_or_404(automation_id, user, db, include_archived=True)
    return automation_service.get_runs(db, automation_id, user.id, limit=limit)


# ------------------------------------------------------------------
# Preview (before anything is persisted)
# ------------------------------------------------------------------

@router.post("/preview")
def preview_new_automation(
    data: AutomationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Validate an automation draft and show what would happen, without saving."""
    cfg = (
        data.trigger_config.model_dump(exclude_none=True)
        if data.trigger_config else {}
    )
    try:
        # Same validation the create endpoint runs — the preview must not tell
        # the user a draft is fine when creating it would fail.
        automation_service.validate_definition(
            data.trigger_type,
            cfg,
            [c.model_dump() for c in (data.conditions or [])],
            [a.model_dump() for a in (data.actions or [])],
            data.timezone,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    next_run = trigger_engine.compute_next_run(
        data.trigger_type, cfg, timezone_name=data.timezone
    )
    return {
        "valid": True,
        "name": data.name,
        "trigger_type": data.trigger_type,
        "trigger_config": cfg,
        "timezone": data.timezone,
        "next_run_at": next_run.isoformat() if next_run else None,
        "actions": [a.model_dump() for a in (data.actions or [])],
        "conditions": [c.model_dump() for c in (data.conditions or [])],
        "estimated_action_count": len(data.actions or []),
        "failure_policy": data.failure_policy,
    }


@router.get("/{automation_id}/preview")
def preview_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Preview next scheduled run and planned actions without executing."""
    automation = _get_automation_or_404(automation_id, user, db)
    return automation_service.preview(automation)


# ------------------------------------------------------------------
# Event Dispatcher (for testing / internal webhooks)
# ------------------------------------------------------------------

@router.post("/event")
def fire_event(
    event: AutomationEvent,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Fire a named event and trigger any matching event-based automations."""
    runs = automation_service.fire_event(
        db,
        user_id=user.id,
        event_type=event.type,
        payload=event.payload,
    )
    return {
        "event_type": event.type,
        "automations_triggered": len(runs),
        "run_ids": [r.id for r in runs],
    }


# ------------------------------------------------------------------
# Legacy execute endpoint (kept for backward compat)
# ------------------------------------------------------------------

@router.post("/{automation_id}/execute")
def execute_automation_legacy(
    automation_id: int,
    event: AutomationEvent,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Legacy endpoint — prefer /{id}/run for manual execution."""
    automation = _get_automation_or_404(automation_id, user, db)
    run = automation_service.run_now(db, automation)
    return {
        "automation_id": automation.id,
        "automation_name": automation.name,
        "run_id": run.id,
        "status": run.status,
    }
