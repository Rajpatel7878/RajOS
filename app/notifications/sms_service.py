class SMSService:


    def send_sms(self, phone, message):

        return {
            "service": "sms",
            "phone": phone,
            "message": message,
            "status": "sent"
        }
