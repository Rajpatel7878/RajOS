from app.notifications.sms_service import SMSService
from app.notifications.push_service import PushService


class NotificationManager:


    def __init__(self):

        self.sms = SMSService()
        self.push = PushService()


    def send_task_reminder(
        self,
        message
    ):

        return {
            "sms": self.sms.send_sms(
                "user_phone",
                message
            ),

            "push": self.push.send_notification(
                "user_device",
                message
            )
        }
