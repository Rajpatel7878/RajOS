class WorkflowEngine:


    def execute(
        self,
        action: str,
        payload: dict | None = None
    ):

        payload = payload or {}

        if action == "create_task":

            return {
                "status": "success",
                "action": "create_task",
                "message": "Task workflow triggered",
                "payload": payload
            }


        elif action == "create_note":

            return {
                "status": "success",
                "action": "create_note",
                "message": "Note workflow triggered",
                "payload": payload
            }


        elif action == "send_notification":

            return {
                "status": "success",
                "action": "send_notification",
                "message": "Notification workflow triggered",
                "payload": payload
            }


        else:

            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }


workflow_engine = WorkflowEngine()
