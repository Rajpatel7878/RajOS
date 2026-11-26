#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notifications Router — manage push subscriptions and send push alerts.

Following RajOS conventions. Endpoints: subscribe, unsubscribe, send-test, summary, task-summary, register-fcm-token.
"""

import logging
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas

class PushSubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    device_label: Optional[str] = "Browser"


class FCMTokenRequest(BaseModel):
    token: str  # FCM registration token


# Endpoints

@router.post("/subscribe")
def subscribe(
    req: PushSubscribeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Save browser push subscription for the authenticated user."""
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


@router.post("/register-fcm-token")
def register_fcm_token(
    req: FCMTokenRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register FCM token for Android device.

    Stores the Firebase Cloud Messaging registration token
    for the authenticated user's device.
    """
    # Find an existing subscription for this token, otherwise reuse the user's
    # first subscription or create an FCM-only device entry.
    sub = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.push_token == req.token,
    ).first()

    if not sub:
        sub = db.query(PushSubscription).filter(
            PushSubscription.user_id == user.id
        ).first()

    if not sub:
        # endpoint / p256dh / auth are NOT NULL in the model even for FCM-only devices
        sub = PushSubscription(
            user_id=user.id,
            endpoint=f"fcm:{req.token}",
            p256dh="n/a",
            auth="n/a",
            device_label="Android",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

    # Store the FCM token
    sub.push_token = req.token
    db.commit()
    db.refresh(sub)

    logger.info("FCM token registered for user %s: token=%s...", user.id, req.token[:20] if len(req.token) > 20 else req.token)

    return {
        "message": "FCM token registered successfully",
        "push_token": sub.push_token,
        "device_id": sub.id,
    }


@router.post("/send-test")
def send_test(
    req: SendTestRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a test push notification to all of the user devices.

    Sends via both Web Push and FCM to all registered devices.
    Returns counts for each channel.
    """
    # Send via Web Push
    webpush_result = {"status": "no_subscriptions", "sent": 0}
    try:
        from app.database.connection import SessionLocal as SessionLocal2
        db2 = SessionLocal2()
        webpush_result = push_service.send_to_user_webpush(user.id, db2, req.title, req.body)
        db2.close()
    except Exception as e:
        webpush_result = {"status": "error", "reason": str(e)}

    # Send via FCM
    fcm_result = {"status": "no_subscriptions", "sent": 0}
    try:
        from app.database.connection import SessionLocal as SessionLocal3
        db3 = SessionLocal3()
        fcm_result = push_service.send_fcm_to_user(user.id, db3, req.title, req.body)
        db3.close()
    except Exception as e:
        fcm_result = {"status": "error", "reason": str(e)}

    return {
        "message": "Test notification processed",
        "webpush": webpush_result,
        "fcm": fcm_result,
    }


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
        Task.due_date is not None,
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
    """Manually trigger a task summary push notification.

    Sends task summary via both Web Push and FCM to all user devices.
    """
    # Send via FCM
    fcm_result = push_service.send_task_summary_fcm(user.id, db)

    # Send via Web Push
    webpush_result = {"status": "no_subscriptions", "sent": 0}
    try:
        from app.database.connection import SessionLocal as SessionLocal2
        db2 = SessionLocal2()
        webpush_result = push_service.send_task_summary_webpush(user.id, db2)
        db2.close()
    except Exception as e:
        webpush_result = {"status": "error", "reason": str(e)}

    sent_count = 0
    if fcm_result.get("status") == "completed":
        sent_count += fcm_result.get("sent", 0)
    if webpush_result.get("status") in ("completed",):
        sent_count += webpush_result.get("sent", 0)

    return {
        "message": f"Task summary sent via {sent_count} channel(s)" if sent_count > 0 else "No subscriptions found",
        "sent": sent_count,
        "fcm": fcm_result,
        "webpush": webpush_result,
    }