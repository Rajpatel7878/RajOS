"""
Notifications Router — manage push subscriptions and send push alerts.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import SessionLocal
from app.models.user import User
from app.models.task import Task
from app.models.push_subscription import PushSubscription
from app.security.dependencies import get_current_user
from app.services.push_service import push_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schemas ──────────────────────────────────────────────────────────────────

class PushSubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    device_label: Optional[str] = "Browser"


class SendTestRequest(BaseModel):
    title: Optional[str] = "🔔 RajOS Test Notification"
    body: Optional[str] = "Push notifications are working!"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/subscribe")
def subscribe(
    req: PushSubscribeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Save browser push subscription for the authenticated user."""
    # Avoid duplicate subscriptions from the same endpoint
    existing = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == req.endpoint,
    ).first()

    if existing:
        existing.p256dh = req.p256dh
        existing.auth = req.auth
        existing.device_label = req.device_label
        db.commit()
        return {"message": "Subscription updated", "id": existing.id}

    sub = PushSubscription(
        user_id=user.id,
        endpoint=req.endpoint,
        p256dh=req.p256dh,
        auth=req.auth,
        device_label=req.device_label,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"message": "Subscribed successfully", "id": sub.id}


@router.delete("/unsubscribe")
def unsubscribe(
    endpoint: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Remove a push subscription."""
    sub = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == endpoint,
    ).first()
    if sub:
        db.delete(sub)
        db.commit()
    return {"message": "Unsubscribed"}


@router.post("/send-test")
def send_test(
    req: SendTestRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a test push notification to all of the user devices."""
    sent = push_service.send_to_user(
        user.id, db,
        title=req.title,
        body=req.body,
        url="/dashboard",
    )
    return {"message": f"Test notification sent to {sent} device(s)", "sent": sent}


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return task summary counts for the notification bell."""
    now = datetime.utcnow()
    total = db.query(Task).filter(Task.user_id == user.id).count()
    completed = db.query(Task).filter(
        Task.user_id == user.id, Task.completed == True
    ).count()
    pending = db.query(Task).filter(
        Task.user_id == user.id, Task.completed == False
    ).count()
    overdue = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == False,
        Task.due_date != None,
        Task.due_date < now,
    ).count()
    due_today = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == False,
        Task.due_date >= now.replace(hour=0, minute=0, second=0),
        Task.due_date <= now.replace(hour=23, minute=59, second=59),
    ).count()

    subscriptions = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id
    ).count()

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "due_today": due_today,
        "subscriptions": subscriptions,
        "push_enabled": subscriptions > 0,
    }


@router.post("/task-summary")
def send_task_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Manually trigger a task summary push notification."""
    ok = push_service.send_task_summary(user.id, db)
    return {
        "message": "Task summary sent" if ok else "No subscriptions found",
        "sent": ok,
    }
