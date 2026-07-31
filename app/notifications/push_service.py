class PushService:


    def send_notification(self, device, message):

        return {
            "service": "push",
            "device": device,
            "message": message,
            "status": "sent"
        }
