"""
Push Notification Service — sends Web Push notifications to subscribed browsers.
Uses pywebpush (VAPID). Works even when the user tab/laptop is closed.
"""

import os
import json
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PushService:
    """Manages sending Web Push notifications to user devices."""

    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
    VAPID_CLAIMS = {"sub": "mailto:admin@rajos.app"}

    def _get_webpusher(self):
        """Lazy import pywebpush."""
        try:
            from pywebpush import webpush, WebPushException
            return webpush, WebPushException
        except ImportError:
            return None, None

    def send(
        self,
        endpoint: str,
        p256dh: str,
        auth_key: str,
        title: str,
        body: str,
        icon: str = "/icon-192.png",
        badge: str = "/icon-96.png",
        url: str = "/",
        tag: Optional[str] = None,
    ) -> bool:
        """Send a push notification to a single subscription."""
        webpush, WebPushException = self._get_webpusher()
        if webpush is None:
            # pywebpush not installed — log and skip gracefully
            logger.warning("pywebpush not installed. Notification not sent: %s", title)
            return False

        if not self.VAPID_PRIVATE_KEY:
            logger.warning("VAPID_PRIVATE_KEY not set. Notification skipped.")
            return False

        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": icon,
            "badge": badge,
            "url": url,
            "tag": tag or title,
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        })

        try:
            webpush(
                subscription_info={
                    "endpoint": endpoint,
                    "keys": {"p256dh": p256dh, "auth": auth_key},
                },
                data=payload,
                vapid_private_key=self.VAPID_PRIVATE_KEY,
                vapid_claims=dict(self.VAPID_CLAIMS),
            )
            return True
        except Exception as exc:
            logger.error("Push notification failed: %s", exc)
            return False

    def send_to_user(self, user_id: int, db, title: str, body: str, url: str = "/tasks") -> int:
        """Send push to ALL subscriptions for a user. Returns count sent."""
        from app.models.push_subscription import PushSubscription

        subscriptions = db.query(PushSubscription).filter(
            PushSubscription.user_id == user_id
        ).all()

        sent = 0
        for sub in subscriptions:
            if self.send(sub.endpoint, sub.p256dh, sub.auth, title, body, url=url):
                sent += 1
        return sent

    def send_task_summary(self, user_id: int, db) -> bool:
        """Send a push with the user task summary counts."""
        from app.models.task import Task

        total = db.query(Task).filter(Task.user_id == user_id).count()
        completed = db.query(Task).filter(
            Task.user_id == user_id, Task.completed == True
        ).count()
        pending = total - completed

        now = datetime.utcnow()
        overdue = db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date != None,
            Task.due_date < now,
        ).count()

        body_parts = [f"✅ {completed} done  ·  🕐 {pending} pending"]
        if overdue:
            body_parts.append(f"  ·  🔴 {overdue} overdue")

        sent = self.send_to_user(
            user_id, db,
            title="📊 RajOS Task Summary",
            body=" ".join(body_parts),
            url="/tasks",
        )
        return sent > 0


push_service = PushService()
