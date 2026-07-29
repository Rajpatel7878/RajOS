from app.notifications.sms_service import SMSService
from app.notifications.push_service import PushService


class NotificationManager:


    def __init__(self):

        self.sms = SMSService()
        self.push = PushService()


    def send_task_reminder(
        self,
        user,
        message
    ):

        if not user.notifications_enabled:
            return {
                "status": "notifications disabled"
            }


        return {
            "sms": self.sms.send_sms(
                user.phone_number,
                message
            ),

            "push": self.push.send_notification(
                user.device_id,
                message
            )
        }
